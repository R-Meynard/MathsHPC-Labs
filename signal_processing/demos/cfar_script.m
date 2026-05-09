% =============================================================
% CA-CFAR — Constant False Alarm Rate (Cell Averaging)
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% Description : Détection adaptative de cibles dans un spectre
%               radar bruité — algorithme fondamental du
%               traitement du signal radar
% =============================================================

% --- Paramètres ---
N        = 256;   % nombre de cellules
Pfa      = 1e-3;  % probabilité de fausse alarme
n_guard  = 2;     % cellules de garde
n_train  = 10;    % cellules d'entraînement

% --- Signal simulé : bruit + cibles ---
bruit    = randn(1, N);
signal   = bruit;
signal(80)  = signal(80)  + 10;  % cible 1
signal(160) = signal(160) + 12;  % cible 2

% --- Puissance ---
P = signal .^ 2;

% --- Seuil CFAR ---
alpha    = n_train * (Pfa^(-1/n_train) - 1);
seuil    = zeros(1, N);
detections = zeros(1, N);

for k = n_train + n_guard + 1 : N - n_train - n_guard
    % Cellules d'entraînement gauche et droite
    gauche = P(k - n_train - n_guard : k - n_guard - 1);
    droite = P(k + n_guard + 1 : k + n_guard + n_train);
    bruit_moy = mean([gauche droite]);
    seuil(k)  = alpha * bruit_moy;

    if P(k) > seuil(k)
        detections(k) = 1;
    end
end

% --- Résultats ---
idx = find(detections);
fprintf('Nombre de détections : %d\n', length(idx));
fprintf('Positions détectées  : ');
disp(idx);