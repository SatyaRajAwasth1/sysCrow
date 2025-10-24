from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.lbfl.src.configs.config_reader import ConfigReader
from src.persistence.models import LogTemplate


class LogTemplateRepository:
    def __init__(self):
        mysql_configs = ConfigReader().get_mysql_configs()

        connection_url = f"mysql+mysqlconnector://{mysql_configs["url"]}"

        engine = create_engine(connection_url)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def save_log_template(self, template_id, template_text):
        """Save a new log template to the MySQL database."""
        try:
            existing_template = self.session.query(LogTemplate).filter(LogTemplate.template_id == template_id).first()

            if existing_template:
                print(f"Template with ID {template_id} already exists.")
            else:
                new_template = LogTemplate(template_id=template_id, template_text=template_text)
                self.session.add(new_template)
                self.session.commit()
                print(f"Log template saved: {new_template}")
        except Exception as e:
            self.session.rollback()
            print(f"Error saving log template: {e}")
        finally:
            self.session.close()

    def get_log_template_by_id(self, template_id):
        """Fetch a log template by ID from the MySQL database."""
        try:
            template = self.session.query(LogTemplate).filter(LogTemplate.template_id == template_id).first()
            return template
        except Exception as e:
            print(f"Error fetching log template: {e}")
            return None
        finally:
            self.session.close()

    def get_all_templates(self, limit=100):
        """Fetch all log templates from the MySQL database."""
        try:
            templates = self.session.query(LogTemplate).limit(limit).all()
            return templates
        except Exception as e:
            print(f"Error fetching log templates: {e}")
            return []
        finally:
            self.session.close()
