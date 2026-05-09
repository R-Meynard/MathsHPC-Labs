% =============================================================
% spectrogram_demo.m — Démonstration STFT sur signal multi-composantes
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

addpath('../functions')
pkg load signal

% --- Signal à deux fréquences ---
Fs  = 1000;
N   = 1024;
t   = (0:N-1) / Fs;
x   = sin(2*pi*50*t) + sin(2*pi*120*t);

% --- Appel de la fonction STFT ---
[S, freqs, temps] = calculer_stft(x, Fs, 256, 128);

% --- Résultats ---
fprintf('STFT calculée\n');
fprintf('Dimensions         : %d x %d\n', size(S,1), size(S,2));
fprintf('Résolution freq    : %.2f Hz\n', freqs(2) - freqs(1));
fprintf('Résolution temps   : %.4f s\n', temps(2) - temps(1));