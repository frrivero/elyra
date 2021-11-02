#
# Copyright 2018-2021 Elyra Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict

import entrypoints

from elyra.metadata.schema import Schemaspace


class Runtimes(Schemaspace):
    RUNTIMES_SCHEMASPACE_ID = "130b8e00-de7c-4b32-b553-b4a52824a3b5"
    RUNTIMES_SCHEMASPACE_NAME = "runtimes"
    RUNTIMES_SCHEMASPACE_DISPLAY_NAME = "Runtimes"

    def __init__(self, *args, **kwargs):
        super().__init__(schemaspace_id=Runtimes.RUNTIMES_SCHEMASPACE_ID,
                         name=Runtimes.RUNTIMES_SCHEMASPACE_NAME,
                         display_name=Runtimes.RUNTIMES_SCHEMASPACE_DISPLAY_NAME,
                         description="Schemaspace for instances of Elyra runtime configurations")


class RuntimeImages(Schemaspace):
    RUNTIME_IMAGES_SCHEMASPACE_ID = "119c9740-d73f-48c6-a97a-599d3acaf41d"
    RUNTIMES_IMAGES_SCHEMASPACE_NAME = "runtime-images"
    RUNTIMES_IMAGES_SCHEMASPACE_DISPLAY_NAME = "Runtime Images"

    def __init__(self, *args, **kwargs):
        super().__init__(schemaspace_id=RuntimeImages.RUNTIME_IMAGES_SCHEMASPACE_ID,
                         name=RuntimeImages.RUNTIMES_IMAGES_SCHEMASPACE_NAME,
                         display_name=RuntimeImages.RUNTIMES_IMAGES_SCHEMASPACE_DISPLAY_NAME,
                         description="Schemaspace for instances of Elyra runtime images configurations")


class CodeSnippets(Schemaspace):
    CODE_SNIPPETS_SCHEMASPACE_ID = "aa60988f-8f7c-4d09-a243-c54ef9c2f7fb"
    CODE_SNIPPETS_SCHEMASPACE_NAME = "code-snippets"
    CODE_SNIPPETS_SCHEMASPACE_DISPLAY_NAME = "Code Snippets"

    def __init__(self, *args, **kwargs):
        super().__init__(schemaspace_id=CodeSnippets.CODE_SNIPPETS_SCHEMASPACE_ID,
                         name=CodeSnippets.CODE_SNIPPETS_SCHEMASPACE_NAME,
                         display_name=CodeSnippets.CODE_SNIPPETS_SCHEMASPACE_DISPLAY_NAME,
                         description="Schemaspace for instances of Elyra code snippets configurations")


class ComponentRegistries(Schemaspace):
    COMPONENT_REGISTRIES_SCHEMASPACE_ID = "ae79159a-489d-4656-83a6-1adfbc567c70"
    COMPONENT_REGISTRIES_SCHEMASPACE_NAME = "component-registries"
    COMPONENT_REGISTRIES_SCHEMASPACE_DISPLAY_NAME = "Component Registries"

    def __init__(self, *args, **kwargs):
        super().__init__(schemaspace_id=ComponentRegistries.COMPONENT_REGISTRIES_SCHEMASPACE_ID,
                         name=ComponentRegistries.COMPONENT_REGISTRIES_SCHEMASPACE_NAME,
                         display_name=ComponentRegistries.COMPONENT_REGISTRIES_SCHEMASPACE_DISPLAY_NAME,
                         description="Schemaspace for instances of Elyra component registries configurations")

        # get set of registered runtimes
        self._runtime_processor_names = set()
        for processor in entrypoints.get_group_all('elyra.pipeline.processors'):
            # load the names of the runtime processors (skip 'local')
            if processor.name == 'local':
                continue
            self._runtime_processor_names.add(processor.name)

    def filter_schema(self, schema: Dict) -> Dict:
        """Replace contents of Runtimes value with set of runtimes if using templated value."""

        # Component-registry requires that `runtime` be a defined property so ensure its existence.
        instance_properties = schema.get('properties', {}).get('metadata', {}).get('properties', {})
        runtime = instance_properties.get('runtime')
        if not runtime:
            raise ValueError(f"{ComponentRegistries.COMPONENT_REGISTRIES_SCHEMASPACE_DISPLAY_NAME} schemas are "
                             f"required to define a 'runtime' (string-valued) property and schema "
                             f"\'{schema.get('name')}\' does not define 'runtime'.")

        if runtime.get('enum') == ["{currently-configured-runtimes}"]:
            runtime['enum'] = list(self._runtime_processor_names)

        # Component catalogs should have an associated 'metadata' class name
        # If none is provided, use the ComponentCatalogMetadata class, which implements
        # post_save and post_delete hooks for improved component caching performance
        if not schema.get('metadata_class_name'):
            schema['metadata_class_name'] = "elyra.pipeline.component_metadata.ComponentCatalogMetadata"

        return schema
