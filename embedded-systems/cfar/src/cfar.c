/*
 * cfar.c — Implémentation OS-CFAR
 *
 * Portage C pur de os_cfar_c_impl.cc (kit-cel/gr-radar, GPL-3.0)
 * Contexte : étude SR3D-NG — Thales Limours
 *
 * Différences par rapport à l'original C++ :
 *   - Pas de dépendance GNU Radio (pas de pmt, pas de tagged_stream_block)
 *   - Pas d'allocation dynamique en chemin critique (tableau statique)
 *   - Interface C pure (linkable depuis C et C++)
 *   - Tri par insertion au lieu de std::sort (adapté à de petites fenêtres)
 */

#include "cfar.h"
#include <math.h>
#include <string.h>

/* Taille maximale de la fenêtre de référence (2 * n_compare max) */
#define CFAR_MAX_WINDOW 256

/* -------------------------------------------------------------------------
 * cfar_power — Puissance d'un complexe
 * -------------------------------------------------------------------------
 * Équivalent de std::pow(std::abs(in[k]), 2) dans gr-radar.
 * On évite sqrtf() (inutile pour comparer des puissances).
 */
float cfar_power(cfar_complex_t c)
{
    return c.re * c.re + c.im * c.im;
}

/* -------------------------------------------------------------------------
 * cfar_sort_floats — Tri par insertion
 * -------------------------------------------------------------------------
 * O(n²) mais n ≤ 2*n_compare (typiquement 32-64 éléments).
 * Préférable à qsort() sur de petits tableaux : pas d'overhead de pointeur
 * de fonction, meilleure localité cache.
 *
 * Dans gr-radar : std::sort(d_hold_samp.begin(), d_hold_samp.end())
 */
void cfar_sort_floats(float *arr, int n)
{
    int i, j;
    float key;
    for (i = 1; i < n; i++) {
        key = arr[i];
        j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

/* -------------------------------------------------------------------------
 * cfar_detect — Détection OS-CFAR principale
 * -------------------------------------------------------------------------
 * Portage direct de os_cfar_c_impl::work() de gr-radar.
 *
 * Fenêtre de référence pour la case k :
 *
 *   [k-N-G ... k-G-1] [k-G ... k-1] [k] [k+1 ... k+G] [k+G+1 ... k+N+G]
 *    <-- N cellules -->  <-- G garde-->    <-- G garde-->  <-- N cellules -->
 *
 * N = n_compare, G = n_guard
 * Le seuil est la valeur à l'index floor(2N * rel_threshold) du tableau trié.
 */
int cfar_detect(const cfar_complex_t *in,
                int                   n_in,
                const cfar_params_t  *params,
                cfar_detection_t     *detections,
                int                   max_det)
{
    /* Tableau statique pour la fenêtre de référence — pas de malloc */
    float   window[CFAR_MAX_WINDOW];
    int     n_det = 0;
    int     consecutive = 0;
    int     k, l, w;
    float   pwr_cell, threshold;
    int     os_index;
    int     window_size;

    if (!in || !params || !detections || n_in <= 0 || max_det <= 0)
        return 0;

    window_size = 2 * params->n_compare;
    if (window_size > CFAR_MAX_WINDOW)
        window_size = CFAR_MAX_WINDOW;

    os_index = (int)((float)(window_size - 1) * params->rel_threshold);
    if (os_index < 0) os_index = 0;
    if (os_index >= window_size) os_index = window_size - 1;

    for (k = 0; k < n_in; k++) {

        /* --- Collecte de la fenêtre de référence --- */
        w = 0;
        for (l = 1; l <= params->n_compare && w < CFAR_MAX_WINDOW - 1; l++) {

            /* Côté gauche : case k - l - n_guard */
            int left = k - l - params->n_guard;
            window[w++] = (left >= 0) ? cfar_power(in[left]) : 0.0f;

            /* Côté droit : case k + l + n_guard */
            int right = k + l + params->n_guard;
            window[w++] = (right < n_in) ? cfar_power(in[right]) : 0.0f;
        }

        /* --- Tri de la fenêtre (OS = Ordered Statistics) --- */
        cfar_sort_floats(window, w);

        /* --- Calcul du seuil adaptatif --- */
        threshold = window[os_index] * params->mult_threshold;

        /* --- Test de détection --- */
        pwr_cell = cfar_power(in[k]);

        if (pwr_cell > threshold) {

            /* Fusion des détections consécutives (pic le plus fort conservé)
             * Portage de la logique merge_consecutive de gr-radar */
            if (params->merge_consecutive && consecutive && n_det > 0) {
                if (detections[n_det - 1].power < pwr_cell) {
                    /* Remplace la détection précédente par la plus forte */
                    detections[n_det - 1].bin       = k;
                    detections[n_det - 1].power     = pwr_cell;
                    detections[n_det - 1].threshold = threshold;
                }
                /* sinon on garde la précédente et on ignore celle-ci */
            } else {
                /* Nouvelle détection */
                if (n_det < max_det) {
                    detections[n_det].bin       = k;
                    detections[n_det].power     = pwr_cell;
                    detections[n_det].threshold = threshold;
                    n_det++;
                }
            }
            consecutive = 1;

        } else {
            consecutive = 0;
        }
    }

    return n_det;
}