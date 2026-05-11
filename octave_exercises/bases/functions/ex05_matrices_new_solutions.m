% =============================================================
% exo5_matrices.m - Operations sur les matrices
% Auteur : Rolih MEYNARD
% Projet : MathsHPC - Octave Exercises
% Date : Mai 2026
% =============================================================

function ex05_matrices_new_solutions(M)
% EX05_MATRICES_NEW_SOLUTIONS - Affiche les proprietes d une matrice%
% Entree :
% M - matrice numerique carree

    [nb_lignes, nb_colonnes] = size(M);
    fprintf('Dimensions : %d x %d \n', nb_lignes, nb_colonnes);

    fprintf('Transposee :\n');
    disp(transpose(M));

    fprintf('Determinant : %0.2f\n', det(M));
    fprintf('Trace : %d\n', trace(M));

    fprintf('Somme colonnes : ');
    disp(sum(M, 1));
end