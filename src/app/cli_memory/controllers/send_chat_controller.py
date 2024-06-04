class CreateProfessionController(CliMemoryControllerInterface):
    """ Create Profession Controller Class
    """
    def _get_profession_info(self) -> CreateProfessionInputDto:
        name = input("Enter the profession name:")
        description = input("Enter the profession description:")
        return CreateProfessionInputDto(name, description)

    def execute(self):
        """ Execute the create profession controller
        """
        repository = ProfessionInMemoryRepository()
        presenter = CreateProfessionPresenter()
        input_dto = self._get_profession_info()
        use_case = CreateProfessionUseCase(presenter, repository)
        result = use_case.execute(input_dto)
        view = CreateProfessionView()
        view.show(result)