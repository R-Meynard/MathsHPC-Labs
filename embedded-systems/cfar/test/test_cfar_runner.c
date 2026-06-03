/*
 * test_cfar_runner.c — Runner Unity pour la suite de tests CFAR
 *
 * Ce fichier contient le main() et enregistre tous les tests.
 * Pattern standard Unity : séparation test / runner.
 */

#include "unity.h"

/* --- Déclarations externes des tests --- */

/* Groupe 1 — Utilitaires */
extern void test_cfar_power_zero_complex(void);
extern void test_cfar_power_real_only(void);
extern void test_cfar_power_imaginary_only(void);
extern void test_cfar_power_complex(void);
extern void test_cfar_sort_already_sorted(void);
extern void test_cfar_sort_reverse(void);
extern void test_cfar_sort_single_element(void);

/* Groupe 2 — Détection */
extern void test_cfar_no_detection_on_zero_spectrum(void);
extern void test_cfar_detects_single_strong_target(void);
extern void test_cfar_detected_power_is_correct(void);
extern void test_cfar_detects_two_separated_targets(void);
extern void test_cfar_threshold_is_positive(void);
extern void test_cfar_weak_target_not_detected(void);

/* Groupe 3 — Limites spectre */
extern void test_cfar_target_at_spectrum_start(void);
extern void test_cfar_target_at_spectrum_end(void);

/* Groupe 4 — Robustesse */
extern void test_cfar_null_input_returns_zero(void);
extern void test_cfar_null_params_returns_zero(void);
extern void test_cfar_zero_length_returns_zero(void);
extern void test_cfar_respects_max_detections_limit(void);

/* Groupe 5 — Merge consecutive */
extern void test_cfar_merge_consecutive_keeps_strongest(void);
extern void test_cfar_no_merge_gives_multiple_detections(void);

extern void test_cfar_large_n_compare_clamped(void);

int main(void)
{
    UNITY_BEGIN();

    /* Groupe 1 */
    RUN_TEST(test_cfar_power_zero_complex);
    RUN_TEST(test_cfar_power_real_only);
    RUN_TEST(test_cfar_power_imaginary_only);
    RUN_TEST(test_cfar_power_complex);
    RUN_TEST(test_cfar_sort_already_sorted);
    RUN_TEST(test_cfar_sort_reverse);
    RUN_TEST(test_cfar_sort_single_element);

    /* Groupe 2 */
    RUN_TEST(test_cfar_no_detection_on_zero_spectrum);
    RUN_TEST(test_cfar_detects_single_strong_target);
    RUN_TEST(test_cfar_detected_power_is_correct);
    RUN_TEST(test_cfar_detects_two_separated_targets);
    RUN_TEST(test_cfar_threshold_is_positive);
    RUN_TEST(test_cfar_weak_target_not_detected);

    /* Groupe 3 */
    RUN_TEST(test_cfar_target_at_spectrum_start);
    RUN_TEST(test_cfar_target_at_spectrum_end);

    /* Groupe 4 */
    RUN_TEST(test_cfar_null_input_returns_zero);
    RUN_TEST(test_cfar_null_params_returns_zero);
    RUN_TEST(test_cfar_zero_length_returns_zero);
    RUN_TEST(test_cfar_respects_max_detections_limit);

    /* Groupe 5 */
    RUN_TEST(test_cfar_merge_consecutive_keeps_strongest);
    RUN_TEST(test_cfar_no_merge_gives_multiple_detections);

    RUN_TEST(test_cfar_large_n_compare_clamped);

    return UNITY_END();
}