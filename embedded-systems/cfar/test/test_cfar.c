/*
 * test_cfar.c — Suite de tests Unity pour le détecteur OS-CFAR
 *
 * Contexte : étude SR3D-NG — Thales Limours
 *
 * Organisation des tests :
 *
 *   Groupe 1 — Fonctions utilitaires (cfar_power, cfar_sort_floats)
 *   Groupe 2 — Détection sur spectre idéal (1 cible isolée, SNR infini)
 *   Groupe 3 — Comportement aux limites (bruit seul, cible en bord de spectre)
 *   Groupe 4 — Robustesse (paramètres invalides, tableau vide)
 *   Groupe 5 — Fusion de détections consécutives (merge_consecutive)
 *
 * Dans un vrai contexte SR3D-NG, ces tests correspondraient à la validation
 * unitaire (STR) du module de détection, tracée dans DOORS.
 */

#include "unity.h"
#include "../src/cfar.h"
#include <math.h>
#include <string.h>

/* =========================================================================
 * HELPERS — construction de spectres de test
 * ========================================================================= */

/* Spectre vide (bruit zéro) */
static void make_zero_spectrum(cfar_complex_t *spec, int n)
{
    memset(spec, 0, n * sizeof(cfar_complex_t));
}

/* Injecte une cible à la puissance donnée sur la case bin */
static void inject_target(cfar_complex_t *spec, int bin, float amplitude)
{
    spec[bin].re = amplitude;
    spec[bin].im = 0.0f;
}

/* Injecte du bruit blanc uniforme à niveau sigma */
static void inject_noise(cfar_complex_t *spec, int n, float sigma)
{
    int i;
    for (i = 0; i < n; i++) {
        spec[i].re += sigma * 0.7071f;  /* bruit fixe pour reproductibilité */
        spec[i].im += sigma * 0.7071f;
    }
}

/* Paramètres CFAR typiques SR3D-NG (valeurs proches gr-radar simulator_fmcw) */
static cfar_params_t make_default_params(void)
{
    cfar_params_t p;
    p.n_compare        = 8;      /* 8 cellules de référence par côté  */
    p.n_guard          = 2;      /* 2 cellules de garde par côté      */
    p.rel_threshold    = 0.75f;  /* 75e percentile de la fenêtre      */
    p.mult_threshold   = 4.0f;   /* facteur multiplicatif             */
    p.merge_consecutive = 0;
    return p;
}

/* =========================================================================
 * setUp / tearDown — appelés avant/après chaque test par Unity
 * ========================================================================= */

void setUp(void) {}
void tearDown(void) {}

/* =========================================================================
 * GROUPE 1 — Fonctions utilitaires
 * ========================================================================= */

void test_cfar_power_zero_complex(void)
{
    cfar_complex_t c = {0.0f, 0.0f};
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 0.0f, cfar_power(c));
}

void test_cfar_power_real_only(void)
{
    /* |3 + 0j|² = 9 */
    cfar_complex_t c = {3.0f, 0.0f};
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 9.0f, cfar_power(c));
}

void test_cfar_power_imaginary_only(void)
{
    /* |0 + 4j|² = 16 */
    cfar_complex_t c = {0.0f, 4.0f};
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 16.0f, cfar_power(c));
}

void test_cfar_power_complex(void)
{
    /* |3 + 4j|² = 25 */
    cfar_complex_t c = {3.0f, 4.0f};
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 25.0f, cfar_power(c));
}

void test_cfar_sort_already_sorted(void)
{
    float arr[] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    cfar_sort_floats(arr, 5);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 1.0f, arr[0]);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 5.0f, arr[4]);
}

void test_cfar_sort_reverse(void)
{
    float arr[] = {5.0f, 4.0f, 3.0f, 2.0f, 1.0f};
    cfar_sort_floats(arr, 5);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 1.0f, arr[0]);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 2.0f, arr[1]);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 5.0f, arr[4]);
}

void test_cfar_sort_single_element(void)
{
    float arr[] = {42.0f};
    cfar_sort_floats(arr, 1);
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 42.0f, arr[0]);
}

/* =========================================================================
 * GROUPE 2 — Détection sur spectre idéal
 * ========================================================================= */

void test_cfar_no_detection_on_zero_spectrum(void)
{
    /* Spectre nul → aucune détection possible (0 > 0 est faux) */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);
    TEST_ASSERT_EQUAL_INT(0, n);
}

void test_cfar_detects_single_strong_target(void)
{
    /*
     * Scénario : 1 cible forte au centre du spectre, bruit bas.
     * La cible doit être détectée exactement 1 fois.
     *
     * Analogie SR3D-NG : avion à forte RCS dans une case range-Doppler claire.
     */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_noise(spec, 256, 0.1f);  /* bruit faible              */
    inject_target(spec, 128, 10.0f); /* cible forte au centre     */

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    TEST_ASSERT_EQUAL_INT(1, n);
    TEST_ASSERT_EQUAL_INT(128, dets[0].bin);
}

void test_cfar_detected_power_is_correct(void)
{
    /* La puissance reportée doit correspondre à |amplitude|² */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_target(spec, 100, 5.0f);  /* amplitude 5 → puissance 25 */

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    TEST_ASSERT_GREATER_THAN_INT(0, n);
    TEST_ASSERT_FLOAT_WITHIN(1e-4f, 25.0f, dets[0].power);
}

void test_cfar_detects_two_separated_targets(void)
{
    /*
     * 2 cibles séparées par plus de 2*(n_compare+n_guard) cases.
     * Chacune doit générer une détection indépendante.
     *
     * Analogie SR3D-NG : 2 avions à des portées différentes.
     */
    cfar_complex_t spec[512];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 512);
    inject_noise(spec, 512, 0.05f);
    inject_target(spec, 100, 8.0f);   /* cible 1 */
    inject_target(spec, 400, 8.0f);   /* cible 2 — séparée de 300 cases */

    int n = cfar_detect(spec, 512, &p, dets, CFAR_MAX_DETECTIONS);

    TEST_ASSERT_EQUAL_INT(2, n);
}

void test_cfar_threshold_is_positive(void)
{
    /* Le seuil adaptatif doit toujours être positif */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_noise(spec, 256, 1.0f);
    inject_target(spec, 128, 20.0f);

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    int i;
    for (i = 0; i < n; i++) {
        TEST_ASSERT_GREATER_THAN_FLOAT(0.0f, dets[i].threshold);
    }
}

void test_cfar_weak_target_not_detected(void)
{
    /*
     * Cible faible noyée dans du bruit fort → ne doit PAS être détectée.
     * Vérifie que le seuil adaptatif fait son travail.
     *
     * C'est le cas "fausse alarme évitée" — fondamental en radar défense.
     */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_noise(spec, 256, 2.0f);   /* bruit fort */
    inject_target(spec, 128, 0.1f);  /* cible très faible */

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    /* La "cible" au bin 128 ne doit pas être détectée */
    int i, found = 0;
    for (i = 0; i < n; i++) {
        if (dets[i].bin == 128) found = 1;
    }
    TEST_ASSERT_EQUAL_INT(0, found);
}

/* =========================================================================
 * GROUPE 3 — Comportement aux limites du spectre
 * ========================================================================= */

void test_cfar_target_at_spectrum_start(void)
{
    /*
     * Cible au bin 0 — la fenêtre gauche est tronquée (underflow).
     * Les cases manquantes sont remplacées par 0 (comportement gr-radar).
     * Le détecteur ne doit pas crasher et doit détecter la cible.
     */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_target(spec, 0, 10.0f);

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    /* Au moins une détection au bin 0 */
    int i, found = 0;
    for (i = 0; i < n; i++) {
        if (dets[i].bin == 0) found = 1;
    }
    TEST_ASSERT_EQUAL_INT(1, found);
}

void test_cfar_target_at_spectrum_end(void)
{
    /* Cible au dernier bin — fenêtre droite tronquée (overflow). */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    inject_target(spec, 255, 10.0f);

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    int i, found = 0;
    for (i = 0; i < n; i++) {
        if (dets[i].bin == 255) found = 1;
    }
    TEST_ASSERT_EQUAL_INT(1, found);
}

/* =========================================================================
 * GROUPE 4 — Robustesse et paramètres invalides
 * ========================================================================= */

void test_cfar_null_input_returns_zero(void)
{
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    int n = cfar_detect(NULL, 256, &p, dets, CFAR_MAX_DETECTIONS);
    TEST_ASSERT_EQUAL_INT(0, n);
}

void test_cfar_null_params_returns_zero(void)
{
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];

    make_zero_spectrum(spec, 256);
    int n = cfar_detect(spec, 256, NULL, dets, CFAR_MAX_DETECTIONS);
    TEST_ASSERT_EQUAL_INT(0, n);
}

void test_cfar_zero_length_returns_zero(void)
{
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 256);
    int n = cfar_detect(spec, 0, &p, dets, CFAR_MAX_DETECTIONS);
    TEST_ASSERT_EQUAL_INT(0, n);
}

void test_cfar_respects_max_detections_limit(void)
{
    /*
     * Spectre avec beaucoup de cibles mais max_det = 2.
     * Le détecteur ne doit jamais dépasser la limite.
     */
    cfar_complex_t spec[512];
    cfar_detection_t dets[2];
    cfar_params_t p = make_default_params();

    make_zero_spectrum(spec, 512);
    int i;
    for (i = 50; i < 500; i += 30) {
        inject_target(spec, i, 10.0f);
    }

    int n = cfar_detect(spec, 512, &p, dets, 2);
    TEST_ASSERT_LESS_OR_EQUAL_INT(2, n);
}

/* =========================================================================
 * GROUPE 5 — Fusion de détections consécutives
 * ========================================================================= */

void test_cfar_merge_consecutive_keeps_strongest(void)
{
    /*
     * 3 cases consécutives au-dessus du seuil, amplitudes croissantes.
     * Avec merge_consecutive=1, une seule détection sur le pic le plus fort.
     *
     * Analogie SR3D-NG : réponse d'une cible qui déborde sur cases adjacentes
     * (effet de la fenêtre de pondération FFT).
     */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();
    p.merge_consecutive = 1;

    make_zero_spectrum(spec, 256);
    inject_target(spec, 127, 5.0f);   /* voisin gauche   */
    inject_target(spec, 128, 10.0f);  /* pic principal   */
    inject_target(spec, 129, 6.0f);   /* voisin droit    */

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    /* Une seule détection attendue */
    TEST_ASSERT_EQUAL_INT(1, n);
    /* Le pic le plus fort (bin 128, puissance 100) doit être conservé */
    TEST_ASSERT_EQUAL_INT(128, dets[0].bin);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, 100.0f, dets[0].power);
}

void test_cfar_no_merge_gives_multiple_detections(void)
{
    /* Même cas, sans fusion → 3 détections attendues */
    cfar_complex_t spec[256];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();
    p.merge_consecutive = 0;

    make_zero_spectrum(spec, 256);
    inject_target(spec, 127, 5.0f);
    inject_target(spec, 128, 10.0f);
    inject_target(spec, 129, 6.0f);

    int n = cfar_detect(spec, 256, &p, dets, CFAR_MAX_DETECTIONS);

    TEST_ASSERT_EQUAL_INT(3, n);
}

void test_cfar_large_n_compare_clamped(void)
{
    cfar_complex_t spec[64];
    cfar_detection_t dets[CFAR_MAX_DETECTIONS];
    cfar_params_t p = make_default_params();
    p.n_compare = 200;  /* > 128 → déclenche le clamp à CFAR_MAX_WINDOW */

    make_zero_spectrum(spec, 64);
    inject_target(spec, 32, 10.0f);
    cfar_detect(spec, 64, &p, dets, CFAR_MAX_DETECTIONS);
    /* pas de crash = test valide */
}