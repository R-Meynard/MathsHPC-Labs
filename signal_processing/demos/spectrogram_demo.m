% =============================================================
% STFT Demo — Analyse temps-fréquence d'un signal multi-composantes
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% Description : Implémentation manuelle de la STFT par fenêtres
%               glissantes sur un signal à deux fréquences (50 Hz
%               et 120 Hz), dans l'esprit du traitement radar
%               (analyse Doppler multi-cibles)
% =============================================================

pkg load signal

% --- Signal à deux fréquences ---
Fs  = 1000;
N   = 1024;
t   = (0:N-1) / Fs;
x   = sin(2*pi*50*t) + sin(2*pi*120*t);

% --- STFT manuelle par fenêtres ---
L    = 256;   % taille fenêtre
hop  = 128;   % pas
win  = hamming(L);
nb_frames = floor((N - L) / hop) + 1;
S    = zeros(L, nb_frames);

for k = 1:nb_frames
    debut = (k-1)*hop + 1;
    frame = x(debut:debut+L-1) .* win';
    S(:,k) = abs(fft(frame));
end

fprintf('STFT manuelle — taille : %d x %d\n', size(S,1), size(S,2));