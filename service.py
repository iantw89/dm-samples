"""Creates autoscaled, network LB IGM running specified docker image."""

import yaml

# Defaults
SIZE_KEY = "size"
DEFAULT_SIZE = 1

MAX_SIZE_KEY = 'maxSize'
DEFAULT_MAX_SIZE = 1

CONTAINER_IMAGE_KEY = 'containerImage'
DEFAULT_CONTAINER_IMAGE = 'container-vm-v20141208'

DOCKER_ENV_KEY = 'dockerEnv'
DEFAULT_DOCKER_ENV = {}


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if SIZE_KEY not in context.properties:
    context.properties[SIZE_KEY] = DEFAULT_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE
  if CONTAINER_IMAGE_KEY not in context.properties:
    context.properties[CONTAINER_IMAGE_KEY] = DEFAULT_CONTAINER_IMAGE
  if DOCKER_ENV_KEY not in context.properties:
    context.properties[DOCKER_ENV_KEY] = DEFAULT_DOCKER_ENV

  name = context.env['name']
  port = context.properties['port']
  targetPool = context.properties['targetPool']
  zone = context.properties['zone']

  igmName = name + '-igm'
  itName = name + '-it'

  resources = [{
      'name': itName,
      'type': 'container_instance_template.py',
      'properties': {
          CONTAINER_IMAGE_KEY: context.properties[CONTAINER_IMAGE_KEY],
          DOCKER_ENV_KEY: context.properties[DOCKER_ENV_KEY],
          'dockerImage': context.properties['image'],
          'port': port
      }
  }, {
      'name': igmName,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + itName + '.selfLink)',
          'targetSize': context.properties[SIZE_KEY],
          'targetPools': ['$(ref.' + targetPool + '.selfLink)'],
          'zone': zone
      }
  }, {
      'name': name + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'autoscalingPolicy': {
              'maxNumReplicas': context.properties[MAX_SIZE_KEY]
          },
          'target': '$(ref.' + igmName + '.selfLink)',
          'zone': zone
      }
  }]

  return yaml.dump({'resources': resources})

