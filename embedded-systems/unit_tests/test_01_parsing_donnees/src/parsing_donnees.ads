with GNATCOLL.JSON; use GNATCOLL.JSON;

package Parsing_Donnees is

   type Entree_Sortie is record
      Id    : Integer;
      A     : Integer;
      B     : Integer;
      Somme : Integer;
   end record;

   function Lire_Donnees (Chemin : String) return JSON_Array;
   --  Lit le fichier JSON et retourne le tableau brut "donnees"

   function Extraire_Entree (Item : JSON_Value) return Entree_Sortie;
   --  Extrait un enregistrement Entree_Sortie depuis un JSON_Value

end Parsing_Donnees;