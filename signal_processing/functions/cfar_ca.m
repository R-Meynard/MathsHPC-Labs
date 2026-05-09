% =============================================================
% CA-CFAR — Constant False Alarm Rate (Cell Averaging)
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% Description : Détection adaptative de cibles dans un spectre
%               radar bruité — algorithme fondamental du
%               traitement du signal radar
% =============================================================

function [detections, seuil] = cfar_ca(P, n_train, n_guard, Pfa)
% CFAR_CA — Détection CA-CFAR sur un vecteur de puissance
%
% Entrées :
%   P        — vecteur de puissance du spectre (1 x N)
%   n_train  — nombre de cellules d'entraînement de chaque côté
%   n_guard  — nombre de cellules de garde de chaque côté
%   Pfa      — probabilité de fausse alarme cible
%
% Sorties :
%   detections — vecteur binaire (1 = détection, 0 = non)
%   seuil      — vecteur du seuil adaptatif calculé

    N          = length(P);
    alpha      = n_train * (Pfa^(-1/n_train) - 1);
    seuil      = zeros(1, N);
    detections = zeros(1, N);

    for k = n_train + n_guard + 1 : N - n_train - n_guard
        gauche    = P(k - n_train - n_guard : k - n_guard - 1);
        droite    = P(k + n_guard + 1 : k + n_guard + n_train);
        bruit_moy = mean([gauche droite]);
        seuil(k)  = alpha * bruit_moy;

        if P(k) > seuil(k)
            detections(k) = 1;
        end
    end

end