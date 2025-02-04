# ScrapPlano
Esse código cria um pdf resumido com os dados principais dos planos de ensino de cada cadeira do tipo Tópico Especial para facilitar a consulta. 
Opcionalmente, também é possível salvar automaticamente todos os planos de ensino dessas cadeiras na sua máquina selecionando 's' quando questionado no terminal.

## Como Rodar
Apenas abra o terminal e utilize pip, ou outro gerenciador de pacotes de sua preferência, para instalar as dependências. 
Comandos para instalar dependências com pip:
pip install bs4
pip install requests
pip install PyPDF2
pip install fpdf

* Obs: Esse código foi feito com Python 3.11

## Atualizando os horários das cadeiras
No repositório o HTML com os horários das cadeiras do semestre de 2025/1 já está disponível, mas se estiver em um semestre futuro e quiser rodar o código com os horários de cadeiras atualizado precisará baixar o HTML novamente:
 - Entre no portal do aluno e navegue para Aluno --> Informações do Aluno ou Matrícula --> Horários e Vagas por Grupo de Matrícula.
 - Selecione seu curso.
 - Aperte F12 para abrir as ferramenteas de desenvolvedor e navegue para a aba "Console"
 - Escreva "document.documentElement.outerHTML;" e dê enter.
 - Copie o texto retornado e cole em um novo arquivo.
 - Salve o arquivo com o tipo HTML na pasta desse repositório: "ScrapPlano".
 - No início do código altere o trecho "caminho_arquivo_html = 'Cadeiras_2025_1.html'" com o nome do novo arquivo HTML.

 ## Limitações e erros
 - Erro de codificação: Aspas (") são substituidas por (?) pois a biblioteca de criação de pdfs FPDF não suporta encoding utf8 e no processo de converter o texto para o encoding latin-1 acontece esse erro. Talvez usar uma biblioteca mais poderoza que suporta utf-8, como a Reportlab seja melhor, isso também permitiria fazer uma estilização do pdf bem mais detalhada.

 - Leitura da Página:
 A página é salva através da aba de desenvolvimento do navegador pois o menu com os horários de cadeiras é um elemento dinâmico, portanto se salvar ela com o botão direito do mouse (em salvar como), as cadeiras não aparecem no HTML salvo. Acredito que essa é a maneira mais simples, considerando que para ler a página automáticamente seria necessário automatizar o login e a navegação até a seção do portal com os horários das cadeiras.