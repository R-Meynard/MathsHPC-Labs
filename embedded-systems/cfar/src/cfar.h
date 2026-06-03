#ifndef CFAR_H
#define CFAR_H

/*
 * cfar.h — Détecteur OS-CFAR (Ordered Statistics CFAR)
 *
 * Portage C pur de os_cfar_c_impl.cc (kit-cel/gr-radar, GPL-3.0)
 * Contexte : étude SR3D-NG — Thales Limours
 *
 * Principe OS-CFAR :
 *   Pour chaque case k du spectre FFT :
 *     1. Collecter 2*N cellules de référence (N de chaque côté, skip G gardes)
 *     2. Trier par puissance croissante
 *     3. Seuil adaptatif T = ref[floor(2N * rel_thr)] * mult_thr
 *     4. Détection si |in[k]|² > T
 *
 * Par rapport au CA-CFAR classique, l'OS-CFAR est plus robuste aux
 * interférences multiples (plusieurs cibles dans la fenêtre de référence).
 * C'est le choix typique des radars de surveillance militaire (Ground Master).
 */

#include <stddef.h>

/* Nombre maximum de détections par appel à cfar_detect() */
#define CFAR_MAX_DETECTIONS 64

/* Structure représentant un complexe flottant (sortie FFT) */
typedef struct {
    float re;
    float im;
} cfar_complex_t;

/* Structure représentant une détection (plot) issue du CFAR */
typedef struct {
    int   bin;        /* Indice de case fréquentielle                    */
    float power;      /* Puissance absolue : re²+im² de la case détectée */
    float threshold;  /* Seuil adaptatif qui a permis la détection        */
} cfar_detection_t;

/* Paramètres du détecteur OS-CFAR */
typedef struct {
    int   n_compare;       /* Demi-fenêtre de référence (cellules par côté) */
    int   n_guard;         /* Cellules de garde par côté                    */
    float rel_threshold;   /* Index OS relatif [0.0, 1.0]                   */
    float mult_threshold;  /* Facteur multiplicatif sur le seuil            */
    int   merge_consecutive; /* 1 = fusionner les détections consécutives   */
} cfar_params_t;

/*
 * cfar_detect() — Détection OS-CFAR sur un spectre FFT
 *
 * Paramètres :
 *   in          : spectre FFT complexe (tableau de n_in éléments)
 *   n_in        : nombre de cases (typiquement puissance de 2 : 512, 1024...)
 *   params      : paramètres du détecteur
 *   detections  : tableau de sortie (plots détectés)
 *   max_det     : capacité maximale du tableau detections
 *
 * Retourne : nombre de détections (0 si aucune cible)
 */
int cfar_detect(const cfar_complex_t *in,
                int                   n_in,
                const cfar_params_t  *params,
                cfar_detection_t     *detections,
                int                   max_det);

/*
 * cfar_power() — Calcule la puissance d'un complexe (re²+im²)
 * Fonction utilitaire exposée pour les tests.
 */
float cfar_power(cfar_complex_t c);

/*
 * cfar_sort_floats() — Tri par insertion sur un tableau de flottants
 * Exposé pour les tests (vérifie le tri de la fenêtre de référence).
 */
void cfar_sort_floats(float *arr, int n);

#endif /* CFAR_H */