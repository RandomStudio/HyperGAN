import hyperchamber as hc
import tensorflow as tf
import importlib

from hypergan.discriminators import *
from hypergan.encoders import *
from hypergan.generators import *
from hypergan.regularizers import *
from hypergan.samplers import *
from hypergan.trainers import *
from hypergan.losses import *
from hypergan.util import *
import hypergan as hg

# Below are sets of configuration options:
# Each time a new random network is started a random set of configuration variables are selected.
# This is useful for hyperparameter search.  If you want to use a specific configuration use --config

def selector(args):
    selector = hc.Selector()
    selector.set('dtype', tf.float32) #The data type to use in our GAN.  Only float32 is supported at the moment

    # Z encoder configuration
    selector.set('z_dimensions', 40)
    selector.set('z_encoder_base', hg.encoders.linear.config())
    selector.set('z_encoders', [[gaussian.config(), periodic_gaussian.config(), periodic_linear.config()]])

    # Generator configuration
    selector.set("generator", [resize_conv.generator])
    selector.set("generator.z_projection_depth", 512) # Used in the first layer - the linear projection of z
    selector.set("generator.activation", [prelu("g_")]); # activation function used inside the generator
    selector.set("generator.activation.end", [tf.nn.tanh]); # Last layer of G.  Should match the range of your input - typically -1 to 1
    selector.set("generator.fully_connected_layers", 0) # Experimental - This should probably stay 0
    selector.set("generator.final_activation", [tf.nn.tanh]) #This should match the range of your input
    selector.set("generator.resize_conv.depth_reduction", 2) # Divides our depth by this amount every time we go up in size
    selector.set('generator.layer.noise', False) #Adds incremental noise each layer
    selector.set('generator.layer_filter', None) #Add information to g
    selector.set("generator.regularizers.l2.lambda", list(np.linspace(0.1, 1, num=30))) # the magnitude of the l2 regularizer(experimental)
    selector.set("generator.regularizers.layer", [batch_norm_1]) # the magnitude of the l2 regularizer(experimental)
    selector.set('generator.densenet.size', 16)
    selector.set('generator.densenet.layers', 1)

    selector.set("trainer", adam_trainer.config())

    # Discriminator configuration
    discriminators = []
    for i in range(1):
        discriminators.append(pyramid_nostride_fc_discriminator.config(layers=5))
    selector.set("discriminators", [discriminators])

    losses = []
    for i in range(1):
        losses.append(wgan.config())
    selector.set("losses", [losses])

    selector.set('categories', [[]])
    selector.set('categories_lambda', list(np.linspace(.001, .01, num=100)))
    selector.set('category_loss', [False])

    return selector

def random(args):
    return selector(args).random_config()


# This looks up a function by name.   Should it be part of hyperchamber?
#TODO moveme
def get_function(name):
    if name == "function:hypergan.util.ops.prelu_internal":
        return prelu("g_")

    if not isinstance(name, str):
        return name
    namespaced_method = name.split(":")[1]
    method = namespaced_method.split(".")[-1]
    namespace = ".".join(namespaced_method.split(".")[0:-1])
    return getattr(importlib.import_module(namespace),method)

# Take a config and replace any string starting with 'function:' with a function lookup.
#TODO moveme
def lookup_functions(config):
    for key, value in config.items():
        if(isinstance(value, str) and value.startswith("function:")):
            config[key]=get_function(value)
        if(isinstance(value, list) and len(value) > 0 and isinstance(value[0],str) and value[0].startswith("function:")):
            config[key]=[get_function(v) for v in value]

    return config


