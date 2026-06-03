/*
 * rt_demo.c — Démonstration patterns temps réel POSIX
 * Contexte SR3D-NG : pipeline radar BackEnd
 *
 * Simule l'architecture de la chaîne de détection :
 *   Thread FE (haute priorité)  →  queue  →  Thread BE CFAR (priorité moyenne)
 *                                             ↓
 *                                   Thread Supervision (basse priorité)
 *
 * Compilation :
 *   gcc -O2 -Wall -std=c99 -o rt_demo rt_demo.c -lpthread -lrt
 */

#define _GNU_SOURCE
#include <pthread.h>
#include <semaphore.h>
#include <sched.h>
#include <mqueue.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* =========================================================================
 * CONSTANTES
 * ========================================================================= */
#define QUEUE_NAME      "/sr3d_plots"
#define MAX_PLOTS       8
#define CPI_COUNT       5       /* Nombre de CPI simulés */

/* Priorités SCHED_FIFO — pattern SR3D-NG
 * FE (Front End) : priorité max — données brutes temps critique
 * BE (Back End CFAR) : priorité haute — traitement signal
 * SUP (Supervision) : priorité basse — monitoring
 */
#define PRIO_FE         80
#define PRIO_BE_CFAR    70
#define PRIO_SUP        50

/* =========================================================================
 * STRUCTURES
 * ========================================================================= */
typedef struct {
    int    cpi_id;      /* Numéro de CPI (Coherent Processing Interval) */
    int    bin;         /* Case fréquentielle détectée                   */
    float  power;       /* Puissance mesurée                             */
    float  threshold;   /* Seuil CFAR                                    */
    struct timespec ts; /* Timestamp de détection                        */
} plot_t;

/* =========================================================================
 * VARIABLES GLOBALES
 * ========================================================================= */
static mqd_t    g_queue;
static sem_t    g_sem_done;
static int      g_plots_processed = 0;
static pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;

/* =========================================================================
 * UTILITAIRES
 * ========================================================================= */
static void timespec_diff_us(struct timespec *start,
                              struct timespec *end,
                              long *us)
{
    *us = (end->tv_sec - start->tv_sec) * 1000000L
        + (end->tv_nsec - start->tv_nsec) / 1000L;
}

static void sleep_ms(int ms)
{
    struct timespec ts = {0, ms * 1000000L};
    nanosleep(&ts, NULL);
}

/* =========================================================================
 * THREAD FE — Front End (simule l'arrivée des données du radar)
 * Priorité SCHED_FIFO 80 — tâche temps critique
 * ========================================================================= */
static void *thread_fe(void *arg)
{
    (void)arg;
    printf("[FE]  Thread démarré — priorité %d\n", PRIO_FE);

    for (int cpi = 0; cpi < CPI_COUNT; cpi++) {
        /* Simule la période radar : ~170ms (6 tours/sec Ground Master) */
        sleep_ms(170);

        /* Génère 2-3 plots par CPI (simule détections CFAR) */
        int n_plots = 2 + (cpi % 2);
        for (int p = 0; p < n_plots; p++) {
            plot_t plot;
            plot.cpi_id = cpi;
            plot.bin    = 100 + p * 50 + cpi * 10;
            plot.power  = 25.0f + p * 5.0f;
            plot.threshold = 4.0f;
            clock_gettime(CLOCK_MONOTONIC, &plot.ts);

            /* Envoi dans la message queue vers le BE */
            if (mq_send(g_queue, (char *)&plot, sizeof(plot), 0) < 0) {
                perror("[FE]  mq_send failed");
            } else {
                printf("[FE]  CPI %d — plot bin=%d power=%.1f envoyé\n",
                       cpi, plot.bin, plot.power);
            }
        }
    }

    printf("[FE]  Terminé — %d CPI traités\n", CPI_COUNT);
    return NULL;
}

/* =========================================================================
 * THREAD BE CFAR — Back End traitement signal
 * Priorité SCHED_FIFO 70 — tâche haute priorité
 * ========================================================================= */
static void *thread_be_cfar(void *arg)
{
    (void)arg;
    printf("[BE]  Thread démarré — priorité %d\n", PRIO_BE_CFAR);

    plot_t plot;
    struct timespec ts_recv;
    long latency_us;
    int total = 0;

    while (1) {
        /* Attente bloquante sur la queue — libère le CPU */
        ssize_t ret = mq_receive(g_queue,
                                 (char *)&plot, sizeof(plot), NULL);
        if (ret < 0) break;

        clock_gettime(CLOCK_MONOTONIC, &ts_recv);
        timespec_diff_us(&plot.ts, &ts_recv, &latency_us);

        /* Traitement CFAR simulé */
        printf("[BE]  Plot reçu — bin=%d power=%.1f latence=%ld µs\n",
               plot.bin, plot.power, latency_us);

        /* Mise à jour compteur thread-safe */
        pthread_mutex_lock(&g_mutex);
        g_plots_processed++;
        total = g_plots_processed;
        pthread_mutex_unlock(&g_mutex);

        /* Fin de session : CPI_COUNT CPIs × ~2.5 plots = ~12 plots */
        if (total >= CPI_COUNT * 2) {
            sem_post(&g_sem_done);
            break;
        }
    }

    printf("[BE]  Terminé — %d plots traités\n", total);
    return NULL;
}

/* =========================================================================
 * THREAD SUPERVISION — monitoring du pipeline
 * Priorité SCHED_OTHER (non-RT) — tâche de fond
 * ========================================================================= */
static void *thread_supervision(void *arg)
{
    (void)arg;
    printf("[SUP] Thread démarré — priorité basse (SCHED_OTHER)\n");

    for (int i = 0; i < 10; i++) {
        sleep_ms(100);
        pthread_mutex_lock(&g_mutex);
        int n = g_plots_processed;
        pthread_mutex_unlock(&g_mutex);
        printf("[SUP] Monitoring : %d plots traités\n", n);
    }

    return NULL;
}

/* =========================================================================
 * MAIN
 * ========================================================================= */
static pthread_t create_rt_thread(void *(*fn)(void *),
                                   int policy, int priority)
{
    pthread_t tid;
    pthread_attr_t attr;
    struct sched_param sp;

    pthread_attr_init(&attr);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_attr_setschedpolicy(&attr, policy);
    sp.sched_priority = priority;
    pthread_attr_setschedparam(&attr, &sp);

    if (pthread_create(&tid, &attr, fn, NULL) != 0) {
        /* Fallback sans RT si pas root */
        pthread_attr_setschedpolicy(&attr, SCHED_OTHER);
        sp.sched_priority = 0;
        pthread_attr_setschedparam(&attr, &sp);
        pthread_create(&tid, &attr, fn, NULL);
        printf("[WARN] Pas de privilèges RT — SCHED_OTHER utilisé\n");
    }

    pthread_attr_destroy(&attr);
    return tid;
}

int main(void)
{
    printf("=== Pipeline RT SR3D-NG — démonstration POSIX ===\n\n");

    /* --- Message queue FE → BE --- */
    struct mq_attr qa;
    qa.mq_flags   = 0;
    qa.mq_maxmsg  = MAX_PLOTS;
    qa.mq_msgsize = sizeof(plot_t);
    qa.mq_curmsgs = 0;

    mq_unlink(QUEUE_NAME);  /* Nettoie une queue résiduelle */
    g_queue = mq_open(QUEUE_NAME, O_CREAT | O_RDWR, 0644, &qa);
    if (g_queue == (mqd_t)-1) {
        perror("mq_open"); return 1;
    }

    sem_init(&g_sem_done, 0, 0);

    /* --- Création des threads --- */
    pthread_t t_sup  = create_rt_thread(thread_supervision,
                                         SCHED_OTHER, 0);
    pthread_t t_be   = create_rt_thread(thread_be_cfar,
                                         SCHED_FIFO, PRIO_BE_CFAR);
    pthread_t t_fe   = create_rt_thread(thread_fe,
                                         SCHED_FIFO, PRIO_FE);

    /* --- Attente fin de traitement --- */
    sem_wait(&g_sem_done);

    /* --- Nettoyage --- */
    pthread_cancel(t_sup);
    pthread_join(t_fe,  NULL);
    pthread_join(t_be,  NULL);
    pthread_join(t_sup, NULL);

    mq_close(g_queue);
    mq_unlink(QUEUE_NAME);
    sem_destroy(&g_sem_done);

    printf("\n=== Pipeline terminé — %d plots traités ===\n",
           g_plots_processed);
    return 0;
}
