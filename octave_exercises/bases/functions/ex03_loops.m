% =============================================================
% ex03_loops.m — Table de multiplication via boucle for
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Octave Exercises
% Date    : Mai 2026
% =============================================================

function ex03_loops(n)
% EX03_LOOPS — Affiche la table de multiplication de n de 1 à 10
%
% Entrée :
%   n — nombre entier dont on affiche la table

    for i = 1:10
        fprintf('%d x %d = %d\n', n, i, n*i);
    end

    fprintf('\n');
end