% =============================================================
% appliquer_fenetre_taylor.m — Application fenêtre de Taylor
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Signal Processing
% Date    : Mai 2026
% =============================================================

function x_windowed = appliquer_fenetre_taylor(x, n_lobes, attenuation)
% APPLIQUER_FENETRE_TAYLOR — Applique une fenêtre de Taylor sur un signal
%
% Entrées :
%   x           — signal temporel (vecteur 1 x N)
%   n_lobes     — nombre de lobes de la fenêtre
%   attenuation — atténuation des lobes secondaires en dB (ex: -30)
%
% Sorties :
%   x_windowed  — signal après application de la fenêtre

    pkg load signal
    N = length(x);
    w = taylorwin(N, n_lobes, attenuation);
    x_windowed = x .* w';

end