# Projeto final - Laboratório de Bases de dados (Bacharelado em Sistemas de Informação - ICMC USP)
 
### O objetivo do projeto é praticar os conhecimentos estudados durante a disciplina com a criação de um protótipo que seja capaz de manipular os dados e gerar relatórios através de uma interface de boa usabilidade. O projeto utiliza dados relacionados ao esporte Fórmula 1.

Link do repositório: https://github.com/JoaoVitorDio/Projeto_Formula1

### Como executar
#### Pré-Requisitos
* PostgreSQL e PgAdmin4;
* Configure as três variáveis de ambiente necessárias para o projeto em uma cópia do arquivo .env.sample (nomeie esta cópia como ".env"):
	*  DATABASE_NAME = 'nome_da_base_de_dados_criada_no_postgres'
	* DATABASE_PASSWORD = 'senha_do_usuario_no_servidor_do_banco_de_dados'
	* DATABASE_USERNAME = 'usuario_do_postgres'
* Linguagem de programação Python instalada, assim como algum gerenciador de pacotes (pip ou conda, por exemplo);

#### Passo-a-passo
* Executar, no diretório do projeto o seguinte comando: `pip install -r requirements.txt`;
* No diretório `Projeto_Formula1/CreateDatabaseAndLoad)/CreateTablesAndLoad`, siga as instruções no arquivo Load.txt e rode-o por inteiro no PgAdmin4, para criar as tabelas e inserir os dados contidos em `CreateTablesAndLoad/data`;
* Vá ao diretório `Projeto_Formula1/CreateDatabaseAndLoad)/CreateUsersTableAndLoad` e execute os comandos do arquivo `CreateUsersTable.txt` no PgAdmin4;
* Execute todo o código `CreateUsersTableAndLoad.py`.
* Volte ao diretório principal e execute o arquivo `app.py`.
* Abra o navegador na seguinte `URL: Localhost:5000`.
* Execute os arquivos no diretório `Setup` que contenham criação de funções, tabelas, views ou triggers no PgAdmin4.
