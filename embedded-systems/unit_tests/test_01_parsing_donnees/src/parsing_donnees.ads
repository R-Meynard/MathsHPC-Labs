with GNATCOLL.JSON; use GNATCOLL.JSON;

package Parsing_Donnees is

   type Entree_Sortie is record
      Id    : Integer;
      A     : Integer;
      B     : Integer;
      Somme : Integer;
   end record;

   function Lire_Donnees (Path : String) return JSON_Array;
   --  Lit le fichier JSON et retourne le tableau "donnees"

   function Extraire_Entree (Item : JSON_Value) return Entree_Sortie;
   --  Extrait les champs id, a, b, somme d'un élément JSON

end Parsing_Donnees;