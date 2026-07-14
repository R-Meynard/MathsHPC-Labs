with Ada.Text_IO;     use Ada.Text_IO;
with GNATCOLL.JSON;   use GNATCOLL.JSON;
with Parsing_Donnees; use Parsing_Donnees;

procedure Main is
   Items : constant JSON_Array := Lire_Donnees ("data/example-1-donnees.json");
begin
   Put_Line ("Nombre d'entrées :" & Length (Items)'Image);
   New_Line;
   for I in 1 .. Length (Items) loop
      declare
         E : constant Entree_Sortie := Extraire_Entree (Get (Items, I));
      begin
         Put_Line ("id=" & E.Id'Image &
                    "  a=" & E.A'Image &
                    "  b=" & E.B'Image &
                    "  somme=" & E.Somme'Image);
      end;
   end loop;
end Main;