import execution

while True:

    print("\n" + "=" * 60)
    print("MOTEUR DE RECHERCHE LO17")
    print("=" * 60)

    print("1 - Reconstruire tous les fichiers")
    print("2 - Lancer le moteur de recherche")
    print("3 - Quitter")

    choix = input("\nVotre choix : ")

    if choix == "1":

        print("\nReconstruction des fichiers en cours...\n")

        execution.contruction_fichiers()

        print("\nReconstruction terminée ✅")

    elif choix == "2":

        execution.interface_terminal()

    else:

        print("\nChoix invalide.")