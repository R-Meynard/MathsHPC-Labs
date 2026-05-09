% =============================================================
% ex02_check_number.m — Vérification du signe d'un nombre
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Octave Exercises
% Date    : Mai 2026
% =============================================================

function ex02_check_number(n)

% EX02_CHECK_NUMBER — Vérifie et affiche le signe d'un nombre
%
% Entrée :
%   n — nombre entier ou décimal à tester
%
% Exemple d'utilisation :
%   ex02_check_number(5)   -> affiche "5 est : Positif"
%   ex02_check_number(-3)  -> affiche "-3 est : Negatif"
%   ex02_check_number(0)   -> affiche "0 est : Zero"

    if (n > 0)
        fprintf('%d est : Positif\n', n);
    elseif (n < 0)
        fprintf('%d est : Negatif\n', n);
    else   
        fprintf('%d est : Zero\n', n);
    endif
end