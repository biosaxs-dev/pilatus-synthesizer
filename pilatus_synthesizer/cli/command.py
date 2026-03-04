"""Command-line controller.

Runs synthesis in headless (non-GUI) mode.

Original: lib/Synthesizer/CommandController.py
Copyright (c) 2015-2020, SAXS Team, KEK-PF
"""

import os
import logging

from pilatus_synthesizer._keklib.our_exception import OurException
from pilatus_synthesizer._keklib.basic_utils import mkdirs_with_retry
from pilatus_synthesizer.config.settings import set_setting, set_mask, get_setting, get_mask
from pilatus_synthesizer.config.preferences import get_preference
from pilatus_synthesizer.config.development import get_devel_info
from pilatus_synthesizer.core.pilatus_utils import get_data_info
from pilatus_synthesizer.core.image_synthesizer import exec_single_synthesis

logger = logging.getLogger(__name__)


class Controller:

    def __init__(self, opts):
        self.opts = opts

        if opts.in_folder is None:
            raise OurException('-i IN_FOLDER argument is required!')

        if not os.path.exists(opts.in_folder):
            raise OurException('%s does not exist!' % opts.in_folder)

        if not os.path.isdir(opts.in_folder):
            raise OurException('%s is not a folder!' % opts.in_folder)

        self.new_out_folder_created = False
        if opts.out_folder is None:
            out_folder = opts.in_folder + '/Synthesized'

            if not opts.autonum_folders and os.path.exists(out_folder):
                import shutil
                shutil.rmtree(out_folder)

            for i in range(1, 100):
                if not os.path.exists(out_folder):
                    break
                out_folder = opts.in_folder + '/Synthesized(%d)' % i
            else:
                raise OurException('Could not find a free output folder name.')

            mkdirs_with_retry(out_folder)
            opts.out_folder = out_folder
            self.new_out_folder_created = True

        if not os.path.exists(opts.out_folder):
            raise OurException('%s does not exist!' % opts.out_folder)

        if not os.path.isdir(opts.out_folder):
            raise OurException('%s is not a folder!' % opts.out_folder)

        set_setting('in_folder', opts.in_folder)
        set_setting('adj_folder', None)
        set_setting('syn_folder', opts.out_folder)

        direction = getattr(opts, 'direction', None)
        if direction is not None:
            set_setting('positive_direction', direction)
        elif get_setting('positive_direction') is None:
            raise OurException(
                'Positive adjustment direction is not set.\n'
                'Use -d left (KEK-PF) or -d right (SPring-8).'
            )

    def execute(self):
        opts = self.opts
        in_folder = opts.in_folder
        adj_folder = getattr(opts, 'adj_folder', None)
        out_folder = opts.out_folder

        logfile_path = os.path.join(out_folder, 'pilatus-synthesizer.log')
        file_handler = logging.FileHandler(logfile_path)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        )
        logging.getLogger().addHandler(file_handler)

        if self.new_out_folder_created:
            logger.info("New folder '%s' has been created.", out_folder)

        try:
            log_file, mask_file, data_array, _pilatus_counter = get_data_info(
                in_folder, adj_folder, out_folder,
                pilatus_counter=None, counter_id='None',
            )

            if mask_file:
                set_mask(os.path.join(in_folder, mask_file))

            mask = get_mask()
            mask_array = mask.mask_array if mask is not None else None

            direction = get_setting('positive_direction')
            syn_method = get_preference('syn_method')
            min_ratio = get_devel_info('min_ratio')
            adj_output = get_devel_info('adj_output') == 'YES'
            postfix_adj = get_devel_info('postfix_adj')
            postfix_syn = get_preference('postfix_syn')
            algorithm = get_devel_info('adj_algorithm')
            intermediate_results = getattr(opts, 'intermediate_results', False)

            self._run_syntheses(
                data_array, mask_array, direction,
                in_folder, adj_folder, out_folder,
                syn_method, min_ratio, adj_output,
                postfix_adj, postfix_syn, algorithm,
                intermediate_results,
            )
        except Exception:
            logger.exception('Unexpected error during synthesis')
        finally:
            logging.getLogger().removeHandler(file_handler)

    def _run_syntheses(self, data_array, mask_array, direction,
                       in_folder, adj_folder, syn_folder,
                       syn_method, min_ratio, adj_output,
                       postfix_adj, postfix_syn, algorithm,
                       intermediate_results):
        for exec_rec in data_array:
            sample_id = exec_rec[0]
            exec_rec_array = exec_rec[1]
            try:
                base_rec = list(exec_rec_array[0])
                previous_im = None
                valid_value_sum_array = None
                valid_pixel_counter_array = None

                for i, sub_rec in enumerate(exec_rec_array[1:], 1):
                    fkey = '%s_%d' % (sample_id, i)
                    isfinal = (i == len(exec_rec_array) - 1)

                    result = exec_single_synthesis(
                        sample_id, base_rec, fkey, sub_rec, isfinal,
                        mask_array=mask_array,
                        direction=direction,
                        in_folder=in_folder,
                        adj_folder=adj_folder,
                        syn_folder=syn_folder,
                        syn_method=syn_method,
                        min_ratio=min_ratio,
                        adj_output=adj_output,
                        postfix_adj=postfix_adj,
                        postfix_syn=postfix_syn,
                        algorithm=algorithm,
                        intermediate_results=intermediate_results,
                        previous_im=previous_im,
                        valid_value_sum_array=valid_value_sum_array,
                        valid_pixel_counter_array=valid_pixel_counter_array,
                    )

                    base_rec[0] = result['result_array']
                    previous_im = result['previous_im']
                    valid_value_sum_array = result['valid_value_sum_array']
                    valid_pixel_counter_array = result['valid_pixel_counter_array']
                    logger.info('Synthesized %s', fkey)

            except Exception:
                logger.exception('Error processing sample %s', sample_id)
