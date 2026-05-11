function ex04_vectors_new_solutions(v)
% EX04_VECTORS - Operations statistiques sur un vecteur
%
% Entree :
% v - vecteur numerique

    fprintf('Taille : %d\n', length(v));
    fprintf('Somme : %d\n', sum(v));
    fprintf('Moyenne : %.2f\n', mean(v));

    [minvector, posMin] = min(v);
    [maxvector, posMax] = max(v);

    fprintf('Minimum : %d a la position %d\n', minvector, posMin);
    fprintf('Maximum : %d a la position %d\n', maxvector, posMax);
end