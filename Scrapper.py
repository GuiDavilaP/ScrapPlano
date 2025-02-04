from bs4 import BeautifulSoup   # Biblioteca para fazer parsing do html.
import requests                 # Biblioteca para fazer donwload do pdf do plano de ensino.
from PyPDF2 import PdfReader    # Biblioteca para extrair texto do pdf.
from fpdf import FPDF           # Biblioteca para criar PDFs.
import re                       # Biblioteca para fazer busca de padrões em texto.
import os                       # Biblioteca usada para deletar arquivo temporário.

#-------------------------------------------------------------------------
def ParsePagina():
    #--------Leitura do arquivo html--------#
    caminho_arquivo_html = 'Cadeiras_2025_1.html' # Altere para o caminho do html da pagina.

    with open(caminho_arquivo_html, 'r', encoding='utf-8') as file:
        conteudo_html = file.read()

    soup = BeautifulSoup(conteudo_html, 'html.parser')

    #--------Extraindo as cadeiras e os links dos seus respectivos planos de ensino--------#
    tabela_horarios = soup.find('table', id='Horarios')
    #print(tabela_horarios.prettify()) # Exibe a tabela de horários.

    if not tabela_horarios:
        raise Exception('Tabela de horários não encontrada. Verifique o arquivo HTML.')

    # Encontra todas as linhas da tabela que contém a cadeira 'Tópicos Especiais'.
    linhas_topicos = []
    nomes_topicos = []
    
    for tr in tabela_horarios.find_all('tr'):
        primeira_col = tr.find('td')
        if primeira_col and 'TÓPICOS ESPECIAIS' in primeira_col.get_text().upper():
            linhas_topicos.append(tr)
            nomes_topicos.append(primeira_col.get_text().strip())

    # Extrai links dos planos de ensino da cadeiras.
    links_planos = []
    count = 0
    for linha in linhas_topicos:
        colunas = linha.find_all('td')
        penultima_coluna = colunas[-2]
        link_tag = penultima_coluna.find('a', href=True)
        if link_tag:
            link = "https://www1.ufrgs.br" + link_tag['href']
            links_planos.append(link)
        else:
            print(f' Link do Plano de Ensino da cadeira {nomes_topicos[count]} NÃO ENCONTRADO!!!')
        count += 1
    
    return nomes_topicos, links_planos

#-------------------------------------------------------------------------
def ConverteNumRomano(num_romano):
    numero_convert = 0
    pos_char = len(num_romano) - 1
    sinalI = 1
    sinalX = 1
    while pos_char >= 0:
        if num_romano[pos_char] == 'X':
            numero_convert += 10 * sinalX
            sinalI = -1
        elif num_romano[pos_char] == 'V':
            numero_convert += 5
            sinalI = -1
        elif num_romano[pos_char] == 'I':
            numero_convert += 1 * sinalI
        elif num_romano[pos_char] == 'L':
            numero_convert += 50
            sinalX = -1

        pos_char -= 1

    return numero_convert

#-------------------------------------------------------------------------
# Baixa o PDF do plano de ensino e extrai o texto dele.
def ExtraiPlano(link_plano, nome_cadeira, deve_salvar):
    response = requests.get(link_plano)

    # Verifica se a requisição foi bem-sucedida.
    if response.status_code == 200:

        # Salva planos de ensino em uma pasta caso usuário queira.
        if deve_salvar:
            # Converte o número romano para decimal e adiciona no título do arquivo.
            num_topico_romano = re.search(r'\b[IVXL]+\b', nome_cadeira)
            num_topico = ConverteNumRomano(num_topico_romano.group(0))

            # Lê o código da cadeira.
            codigo_cadeira = re.search(r'\b[A-Z]{3}[0-9]{5}\b', nome_cadeira).group(0)

            # Cria a pasta se não existir.
            pasta_planos = 'Planos de ensino'
            if not os.path.exists(pasta_planos):
                os.makedirs(pasta_planos)

            nome_arquivo = os.path.join(pasta_planos, f"{codigo_cadeira}_Tópicos_Especiais_{num_topico_romano.group(0)} ({str(num_topico)}).pdf")      
        else:
            nome_arquivo = 'plano_ensino.pdf'
        
        with open(nome_arquivo, 'wb') as file:
                file.write(response.content)
        
        # Extraindo o texto do PDF.
        texto_completo = ''
        reader = PdfReader(nome_arquivo)
        for page in reader.pages:
            texto_completo += page.extract_text() + '\n'
        
        # Extraindo informações específicas.
        professor = re.search(r'Professor Responsável: (.+)', texto_completo)
        sumula = re.search(r'Súmula\n(.+?)(?=\n[A-Z])', texto_completo, re.DOTALL).group(1).strip()
        objetivos = re.search(r'Objetivos\n(.+?)(?=\nConteúdo Programático)', texto_completo, re.DOTALL).group(1).strip()

        # Remover novas linhas desnecessárias
        sumula = ' '.join(sumula.split())
        objetivos = ' '.join(objetivos.split())

        # Construindo o texto sumarizado.
        plano_texto = f'Nome da Cadeira: {nome_cadeira}\n'
        if professor:
            plano_texto += f'Professor Responsável: {professor.group(1)}\n'
        if sumula:
            plano_texto += f'    Súmula: {sumula}\n'
        if objetivos:
            plano_texto += f'    Objetivos: {objetivos}\n'
        
        print(f'  Plano de Ensino da cadeira {nome_cadeira} extraído com sucesso!')

        # Deleta o arquivo PDF temporário se existir.
        if os.path.exists('plano_ensino.pdf'):
            os.remove('plano_ensino.pdf')

        return plano_texto
    else:
        print(f'  Erro ao baixar o PDF: {response.status_code}')
        return None

#-------------------------------------------------------------------------
def main():
    # Pergunta se os planos de ensino devem ser salvos.
    while(True):
        print(" Deseja salvar os planos de ensinos completos? (s/n): ", end='')
        resposta = input().lower()
        if resposta != 's' and resposta != 'n':
            print(" Resposta inválida. Digite 's' para sim ou 'n' para não.")
        else:
            break
    deve_salvar = (resposta == 's')

    print(" Lendo nomes e links dos planos de ensino...")
    nomes_topicos, links_planos = ParsePagina()

    print(" Lendo planos de ensino...")
    planos_texto = []
    for nome_topico, link_plano in zip(nomes_topicos, links_planos):
        plano_texto = ExtraiPlano(link_plano, nome_topico, deve_salvar)
        if plano_texto:
            planos_texto.append(plano_texto)

    # Salvando todos os planos sumarizados em um único arquivo PDF.
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for plano_texto in planos_texto:
        # Substituir caracteres especiais por seus equivalentes `latin-1` ou removê-los.
        plano_texto = plano_texto.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, plano_texto + '\n\n', align='J')  # Justificar o texto
    pdf.output('Sumário_Planos_Ensino.pdf')

main()