% =============================================================
% taylor_window.m — Démonstration fenêtre de Taylor
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

addpath('../functions')

% --- Paramètres ---
Fs = 1000;
N  = 1024;
f  = 50;

% --- Signal ---
t = (0:N-1) / Fs;
x = sin(2*pi*f*t);

% --- Application fenêtre de Taylor ---
x_windowed = appliquer_fenetre_taylor(x, 4, -30);

% --- FFT sans et avec fenêtre ---
[P_raw,  freqs] = calculer_fft(x, Fs);
[P_wind, ~    ] = calculer_fft(x_windowed, Fs);

% --- Résultats ---
fprintf('Sans fenêtre — pic à : %.1f Hz\n', freqs(P_raw  == max(P_raw)));
fprintf('Avec fenêtre — pic à : %.1f Hz\n', freqs(P_wind == max(P_wind)));