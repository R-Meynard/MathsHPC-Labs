% =============================================================
% FFT Demo — Spectre de puissance d'un signal sinusoïdal
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% Description : Calcul du spectre de puissance d'un signal
%               sinusoïdal via FFT, dans l'esprit du traitement
%               de signaux radar (signaux IQ, détection de cibles)
% =============================================================

pkg load signal

% --- Paramètres du signal ---
Fs = 1000;          % Fréquence d'échantillonnage (Hz)
T  = 1;             % Durée du signal (secondes)
f  = 50;            % Fréquence du signal (Hz)

% --- Génération du signal ---
t = 0:1/Fs:T-1/Fs;          % Vecteur temps
x = sin(2*pi*f*t);           % Signal sinusoïdal à f Hz

% --- Calcul de la FFT ---
N = length(x);
X = fft(x);
P = abs(X/N).^2;             % Spectre de puissance

% --- Vecteur fréquences ---
freqs = (0:N-1) * Fs / N;    % Fréquences correspondantes aux bins FFT

% --- Affichage des résultats ---
fprintf('Fréquence du pic détecté : %.1f Hz\n', freqs(P == max(P)));
disp('10 premières fréquences (Hz) :');
disp(freqs(1:10));