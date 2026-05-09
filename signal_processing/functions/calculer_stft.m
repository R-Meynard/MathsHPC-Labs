% =============================================================
% calculer_stft.m — Calcul de la STFT par fenêtres glissantes
% Auteur  : Rolih MEYNARD
% Projet  : MatheHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

function [S, freqs, temps] = calculer_stft(x, Fs, L, hop)
% CALCULER_STFT — Calcule la STFT d'un signal par fenêtres glissantes
%
% Entrées :
%   x    — signal temporel (vecteur 1 x N)
%   Fs   — fréquence d'échantillonnage (Hz)
%   L    — taille de la fenêtre (nombre d'échantillons)
%   hop  — pas entre deux fenêtres consécutives
%
% Sorties :
%   S      — matrice STFT (L x nb_frames)
%   freqs  — vecteur des fréquences (Hz)
%   temps  — vecteur des instants temporels (secondes)

    N         = length(x);
    win       = hamming(L);
    nb_frames = floor((N - L) / hop) + 1;
    S         = zeros(L, nb_frames);

    for k = 1:nb_frames
        debut      = (k-1)*hop + 1;
        frame      = x(debut:debut+L-1) .* win';
        S(:,k)     = abs(fft(frame));
    end

    freqs = (0:L-1) * Fs / L;
    temps = (0:nb_frames-1) * hop / Fs;

end