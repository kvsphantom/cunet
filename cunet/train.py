import logging
import tensorflow as tf
from cunet.others.utilities import (
    make_earlystopping, make_reduce_lr, make_tensorboard, make_checkpoint,
    make_name, save_dir, write_config
)
from cunet.config import config
from cunet.models.cunet_model import cunet_model
from cunet.models.unet_model import unet_model
from cunet.data_loader import dataset_generator
import os

from cunet.others.lock import get_lock
import manage_gpus as gpl


logger = tf.get_logger()
logger.setLevel(logging.INFO)


def main():
    config.parse_args()
    name = make_name()
    save_path = save_dir('models', name)
    write_config(save_path)
    gpu_id_locked = get_lock()
    logger.info('Starting the computation')

    logger.info('Running training with config %s' % str(config))
    logger.info('Getting the model')
    if config.MODE == 'standard':
        model = unet_model()
    if config.MODE == 'conditioned':
        model = cunet_model()

    logger.info('Preparing the genrators')
    ds_train = dataset_generator()
    ds_val = dataset_generator(val_set=True)

    logger.info('Starting training for %s' % name)
    model.fit(
        ds_train,
        validation_data=ds_val,
        steps_per_epoch=config.N_BATCH,
        epochs=config.N_EPOCH,
        callbacks=[
            make_earlystopping(),
            make_reduce_lr(),
            make_tensorboard(save_path),
            make_checkpoint(save_path)
        ])

    logger.info('Saving model %s' % name)
    model.save(os.path.join(save_path, name+'_final.h5'))
    logger.info('Done!')
    model.summary()

    if gpu_id_locked >= 0:
        gpl.free_lock(gpu_id_locked)
    return


if __name__ == '__main__':
    main()
