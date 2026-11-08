# Guia de Implantação no Ubuntu Linux e Análise da Exigência do Arquivo XML

## 1. Implantação em Máquina Virtual Ubuntu Linux

### 1.1. Pré-requisitos na VM Ubuntu
- Ubuntu Linux (22.04 LTS ou 24.04 LTS)
- Python 3.10+ (`python3`, `python3-venv`, `python3-pip`)
- MySQL Server 8.4 (`mysql-server`)
- Git
- Opcional: Nginx (para proxy reverso na porta 80)

### 1.2. Inspeção Segura do MySQL 8.4 (Antes de Executar Scripts)

> **Importante:** Nunca execute comandos destrutivos (`DROP DATABASE`, `DROP TABLE`) na VM sem antes inspecionar os bancos existentes.

1. Conecte ao MySQL na VM Ubuntu:
   ```bash
   sudo mysql -u root -p
   ```
2. Verifique os bancos e tabelas existentes:
   ```sql
   SHOW DATABASES;
   SELECT VERSION();
   ```
3. Saia do prompt interativo e aplique os scripts não-destrutivos (`CREATE DATABASE IF NOT EXISTS` e `CREATE TABLE IF NOT EXISTS`) na ordem:
   ```bash
   mysql -u root -p < database/01_create_database.sql
   mysql -u root -p < database/02_create_tables.sql
   mysql -u root -p < database/03_insert_data.sql
   ```
4. Crie/configure o usuário da aplicação no MySQL 8.4:
   ```sql
   CREATE USER IF NOT EXISTS 'beauty_user'@'localhost' IDENTIFIED BY 'SUA_SENHA_SEGURA';
   GRANT SELECT, INSERT, UPDATE, DELETE ON beauty_schedule.* TO 'beauty_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 1.3. Configuração da Aplicação e `.env`

```bash
sudo mkdir -p /opt/beautyschedule
sudo chown -R $USER:$USER /opt/beautyschedule
git clone https://github.com/marialuiza-mdealcantara/BeautySchedule.git /opt/beautyschedule
cd /opt/beautyschedule

bash deploy/setup_ubuntu.sh
```

Edite o arquivo `/opt/beautyschedule/.env`:
```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

DB_ENGINE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=beauty_schedule
DB_USER=beauty_user
DB_PASSWORD=SUA_SENHA_SEGURA

DEFAULT_SALAO_ID=1
DEFAULT_USUARIO_ID=1
```

### 1.4. Configuração do Serviço no Linux (`systemd`)

Para manter a API FastAPI em execução contínua e iniciar automaticamente no boot da VM Ubuntu, utilize a unidade `systemd` fornecida em `deploy/beautyschedule.service`:

```bash
sudo cp deploy/beautyschedule.service /etc/systemd/system/beautyschedule.service
sudo systemctl daemon-reload
sudo systemctl enable beautyschedule
sudo systemctl start beautyschedule
sudo systemctl status beautyschedule
```

---

## 2. Esclarecimento Técnico: Arquivo XML vs. Unidade `systemd` (`.service`)

### 2.1. Resultado da Pesquisa no Repositório
Foi realizada inspeção completa de todos os arquivos e commits do repositório (`README.md` e histórico Git). Não há nos arquivos originais nenhuma especificação técnica, schema XSD/DTD ou exemplo detalhando o padrão de arquivo XML mencionado como requisito acadêmico.

### 2.2. Distinção Conceitual Importante
- **Unidade `systemd` (`deploy/beautyschedule.service`)**: No Ubuntu Linux moderno, serviços de sistema são gerenciados pelo `systemd`, cujo formato nativo é **INI-like** (seções `[Unit]`, `[Service]`, `[Install]`), e **não XML**.
- **Arquivo XML de Configuração de Serviço**: Em disciplinas de *SaaS Infrastructure* ou *Arquitetura de Sistemas*, um arquivo XML pode se referir a:
  1. Um **manifesto/descritor arquitetural do serviço SaaS** (documentando camadas, portas, banco de dados e políticas de execução);
  2. Uma definição de serviço de firewall do Linux (`firewalld` em `/etc/firewalld/services/beautyschedule.xml`);
  3. Um arquivo de configuração de gerenciador específico de laboratório/hipervisor (`libvirt` domain XML) ou servidor de aplicação.

### 2.3. Dúvida para Validação com o Professor e Proposta Entregue
Como o formato exato esperado pelo professor ainda não foi especificado:
1. Criamos a unidade real funcional do Ubuntu em `deploy/beautyschedule.service` (formato nativo `systemd`).
2. Criamos uma **proposta de descritor XML** em `deploy/beautyschedule-service-proposal.xml`, devidamente documentada como proposta para validação docente.
3. **Pergunta recomendada para apresentar ao professor:**
   > *"Professor, para a entrega do arquivo XML de configuração do serviço na VM Ubuntu, o senhor espera um descritor arquitetural próprio da aplicação (como o modelo que estruturamos em `deploy/beautyschedule-service-proposal.xml`), um arquivo XML de regra de porta do `firewalld`, ou algum schema específico adotado na disciplina?"*
