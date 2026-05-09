function ex01_basic_operations(a, b)
    
    Somme = a + b;
    Difference = a - b;
    Produit = a * b;
    Quotient = a / b;
    Puissance = a^b;

    fprintf('Somme : %d\n', Somme);
    fprintf('Difference : %d\n', Difference);
    fprintf('Produit : %d\n', Produit);
    fprintf('Quotient : %.2f\n', Quotient);
    fprintf('Puissance : %d\n', Puissance);
end
