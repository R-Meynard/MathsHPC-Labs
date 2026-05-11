% =============================================================
% ex04_vectors.m — Calcul sur un vecteur
% Auteur  : Rolih MEYNARD
% Projet  : MathsHPC — Octave Exercises
% Date    : Mai 2026
% =============================================================

function ex04_vectors(v)

% EX04_VECTORS — Prend en entree un vecteur v et effectue des operations
%
% Entrée :
%   v — vecteur
%
% Exemple d'utilisation :
%   v = [1, 2, 3, 4, 5]
%   ex04_vectors(v)   
%         -> affiche la taille du vecteur : 5
%         -> affiche la somme de ses elements : 1+2+3+4+5 = 15
%         -> affiche la moyenne : 15 / 5 = 3
%         -> affiche le minimum et sa position : 1 à la position 0
%         -> affiche le maximum et sa position : 5 à la position 4

    % Afficher la taille du vecteur
    fprintf('Taille : %d\n', length(v));

    % Afficher la somme des elements du vecteur
    fprintf('Somme : %d\n', sum(v));

     % Afficher la moyenne du vecteur
    fprintf('Moyenne : %0.2f\n', mean(v));

    % Minimum du vecteur
    minvector = min(v);
    maxvector = max(v);
    positionMinVector = 1;
    positionMaxVector = 1;
    for i = 1:length(v)
        if(minvector == v(i))
            positionMinVector = i;
        endif
        if(maxvector == v(i))
            positionMaxVector = i;
        endif
    endfor

    fprintf('Minimum : %d a la postion %d\n', minvector, positionMinVector);
    fprintf('Maximum : %d a la position %d\n', maxvector, positionMaxVector);

end