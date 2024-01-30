"""
Class for generating IIIF manifests based on data retrieved from a SPARQL endpoint.
Metadata is retrieved from the SPARQL endpoint through the use of field definitions.
"""
class IiifManifestGenerator:

    def __init__(self, *, baseUri: str = "http://example.org/manifests/"):
        """
        Initialize the generator.
        """
        self.baseUri = baseUri

    def generate(self, *, id: str, label: str, images: list, metadata: list) -> dict:
        manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": f"{self.baseUri}{id}",
            "items": [],
            "type": "Manifest",
            "label": {
                "none": [label]
            },
            "metadata": metadata,
        }
        manifest['items'] = self.generateImageItems(images)
        return manifest
    
    def generateImageItems(self, images: list) -> list:
        items = []
        for i, image in enumerate(images):
            canvas = {
                "id": "%s/image/%d/canvas" % (self.baseUri, i),
                "type": "Canvas",
                "width": int(image['width']),
                "height": int(image['height']),
                "items": [{
                        "id": "%s/image/%d/canvas/page" % (self.baseUri, i),
                        "type": "AnnotationPage",
                        "items": [{
                            "id": "%s/image/%d/canvas/page/annotation" % (self.baseUri, i),
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "id": "%s/full/max/0/default.jpg" % image['image'],
                                "type": "Image",
                                "format": "image/jpeg",
                                "width": int(image['width']),
                                "height": int(image['height']),
                                "service": [{
                                    "id": image['image'],
                                    "profile": "level1",
                                    "type": "ImageService3"
                                }]
                            },
                            "target": "%s/image/%d/canvas" % (self.baseUri, i)
                        }]
                    }]
            }
            items.append(canvas)
        return items