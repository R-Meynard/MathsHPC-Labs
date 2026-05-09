% =============================================================
% cfar_demo.m — Démonstration algorithme CA-CFAR
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

addpath('../functions')

% --- Génération du signal simulé ---
N      = 256;
bruit  = randn(1, N);
signal = bruit;
signal(80)  = signal(80)  + 10;  % cible 1
signal(160) = signal(160) + 12;  % cible 2
P = signal .^ 2;

% --- Appel de la fonction CFAR ---
[detections, seuil] = cfar_ca(P, 10, 2, 1e-3);

% --- Résultats ---
idx = find(detections);
fprintf('Nombre de détections : %d\n', length(idx));
fprintf('Positions détectées  : ');
disp(idx);