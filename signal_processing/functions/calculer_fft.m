% =============================================================
% calculer_fft.m — Calcul du spectre de puissance via FFT
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

function [P, freqs] = calculer_fft(x, Fs)
% CALCULER_FFT — Calcule le spectre de puissance d'un signal
%
% Entrées :
%   x    — signal temporel (vecteur 1 x N)
%   Fs   — fréquence d'échantillonnage (Hz)
%
% Sorties :
%   P     — spectre de puissance (première moitié uniquement)
%   freqs — vecteur des fréquences correspondantes (Hz)

    N      = length(x);
    X      = fft(x);
    P_full = abs(X/N).^2;

    % Garder uniquement la première moitié — éviter le miroir FFT
    N_half = floor(N/2);
    P      = P_full(1:N_half);
    freqs  = (0:N_half-1) * Fs / N;

end