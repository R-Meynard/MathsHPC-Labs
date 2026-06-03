# Makefile — Projet cfar
# Contexte : étude SR3D-NG — Thales Limours
#
# Usage :
#   make              → compile et lance les tests
#   make test         → idem
#   make clean        → supprime les binaires
#   make valgrind     → lance les tests sous Valgrind (memcheck)
#   make coverage     → rapport de couverture gcov (nécessite lcov)
#
# UNITY_DIR doit pointer vers le clone de ThrowTheSwitch/Unity
# Par défaut : ~/Workspace/Unity (adapte si besoin)

CC      = gcc
CFLAGS  = -Wall -Wextra -Wpedantic -std=c99 -g -O0
CFLAGS += -Wno-unused-parameter

# Chemin vers Unity — modifie si ton clone est ailleurs
UNITY_DIR = $(HOME)/Workspace/Unity

SRC_DIR  = src
TEST_DIR = test

# Sources du projet
SRC_FILES  = $(SRC_DIR)/cfar.c

# Sources des tests
TEST_FILES = $(TEST_DIR)/test_cfar.c \
             $(TEST_DIR)/test_cfar_runner.c

# Unity
UNITY_SRC  = $(UNITY_DIR)/src/unity.c
UNITY_INC  = $(UNITY_DIR)/src

# Includes
INCLUDES = -I$(SRC_DIR) -I$(UNITY_INC)

# Binaire de test
TEST_BIN = test_cfar

# -------------------------------------------------------------------------
.PHONY: all test clean valgrind coverage

all: test

test: $(TEST_BIN)
	@echo ""
	@echo "=== Lancement des tests OS-CFAR ==="
	@./$(TEST_BIN)

$(TEST_BIN): $(SRC_FILES) $(TEST_FILES) $(UNITY_SRC)
	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@ -lm

# -------------------------------------------------------------------------
# Valgrind — détection de fuites mémoire et accès invalides
# Outil présent dans le workbench SW BE Thales (SonarQube équivalent local)
valgrind: $(TEST_BIN)
	@echo "=== Valgrind memcheck ==="
	valgrind --tool=memcheck \
	         --leak-check=full \
	         --track-origins=yes \
	         --error-exitcode=1 \
	         ./$(TEST_BIN)

# -------------------------------------------------------------------------
# AddressSanitizer — alternative rapide à Valgrind (intégré dans GCC)
asan: CFLAGS += -fsanitize=address,undefined
asan: clean $(TEST_BIN)
	@echo "=== AddressSanitizer ==="
	./$(TEST_BIN)

# -------------------------------------------------------------------------
# Couverture de code gcov
coverage: CFLAGS += --coverage
coverage: clean $(TEST_BIN)
	@./$(TEST_BIN)
	@gcov -o . test_cfar-cfar.gcno
	@echo ""
	@echo "Fichier cfar.c.gcov généré — ouvrir pour voir la couverture ligne par ligne"

clean:
	rm -f $(TEST_BIN) *.gcov *.gcda *.gcno
	@echo "Nettoyé."
