with AUnit.Assertions; use AUnit.Assertions;
with GNATCOLL.JSON;    use GNATCOLL.JSON;
with Parsing_Donnees;  use Parsing_Donnees;

package body Parsing_Donnees_Tests is

   overriding function Name (T : Test_Case) return Message_String is
      pragma Unreferenced (T);
   begin
      return Format ("Parsing de example-1-donnees.json");
   end Name;

   overriding procedure Run_Test (T : in out Test_Case) is
      pragma Unreferenced (T);
      Items : constant JSON_Array :=
        Lire_Donnees ("data/example-1-donnees.json");
   begin
      Assert (Length (Items) > 0,
              "Le tableau 'donnees' ne doit pas être vide");

      declare
         Premier : constant Entree_Sortie := Extraire_Entree (Get (Items, 1));
      begin
         Assert (Premier.Somme = Premier.A + Premier.B,
                 "La somme ne correspond pas à a + b pour le premier élément");
      end;
   end Run_Test;

end Parsing_Donnees_Tests;