function ex05_matrices(M)
% EX05_MATRICES - Operations les matrices
%
% Entree :
% m - matrice numerique

    fprintf('Dimensions : %d x %d\n', rows(M), columns(M));

    fprintf('Transpose : \n');
    disp(transpose(M));

    fprintf('Determinant : %.2f\n', det(M));
    fprintf('Trace : %d\n', trace(M));

    fprintf('Somme des colonnes : \n');
    disp(sum(M, 1));

end