% =============================================================
% Fenêtre de Taylor — Réduction des lobes secondaires
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% Description : Application d'une fenêtre de Taylor sur un
%               signal sinusoïdal avant calcul FFT, dans
%               l'esprit du traitement radar (projet COBRA)
% =============================================================

pkg load signal

% --- Paramètres ---
Fs  = 1000;
N   = 1024;
f   = 50;

% --- Signal sinusoïdal ---
t = (0:N-1) / Fs;
x = sin(2*pi*f*t);

% --- Fenêtre de Taylor (via package signal) ---
w = taylorwin(N, 4, -30);   % 4 lobes, atténuation -30 dB

% --- Application de la fenêtre ---
x_windowed = x .* w';

% --- FFT sans et avec fenêtre ---
P_raw      = abs(fft(x) / N).^2;
P_windowed = abs(fft(x_windowed) / N).^2;

% --- Affichage comparatif ---
freqs = (0:N-1) * Fs / N;
fprintf('Sans fenêtre  — pic à : %.1f Hz\n', freqs(P_raw == max(P_raw)));
fprintf('Avec fenêtre  — pic à : %.1f Hz\n', freqs(P_windowed == max(P_windowed)));