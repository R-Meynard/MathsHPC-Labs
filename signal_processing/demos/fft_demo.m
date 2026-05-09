% =============================================================
% fft_demo.m — Script de démonstration FFT
% Auteur  : Rolih MEYNARD
% Projet  : MatheHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

% Ajout du chemin vers les fonctions
addpath('../functions')

% --- Paramètres ---
Fs = 1000;
N  = 1024;
f  = 50;

% --- Génération du signal ---
t = (0:N-1) / Fs;
x = sin(2*pi*f*t);

% --- Appel de la fonction FFT ---
[P, freqs] = calculer_fft(x, Fs);

% --- Affichage ---
fprintf('Fréquence du pic détecté : %.1f Hz\n', freqs(P == max(P)));