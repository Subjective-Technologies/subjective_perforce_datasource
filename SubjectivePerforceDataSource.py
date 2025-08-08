import os
import subprocess
import requests
from urllib.parse import urljoin

from subjective_abstract_data_source_package import SubjectiveDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class SubjectivePerforceDataSource(SubjectiveDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        server = self.params['server']
        user = self.params['user']
        password = self.params['password']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for Perforce server '{server}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            os.environ['P4PORT'] = server
            os.environ['P4USER'] = user
            os.environ['P4PASSWD'] = password

            BBLogger.log(f"Fetching repositories for Perforce server '{server}'.")
            subprocess.run(['p4', 'sync'], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully synchronized Perforce workspace.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error syncing Perforce workspace: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error syncing Perforce workspace: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return SVG icon content, preferring a local icon.svg in the plugin folder."""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        try:
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="#0060FF"/><text x="12" y="14" font-size="10" fill="#fff" text-anchor="middle">P4</text></svg>'

    def get_connection_data(self):
        """
        Return the connection type and required fields for Perforce.
        """
        return {
            "connection_type": "Perforce",
            "fields": ["server", "user", "password", "target_directory"]
        }


