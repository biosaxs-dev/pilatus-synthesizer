"""GUI wrapper around the core image synthesis engine.

Drives the ActionWindow + background thread for action=3 (synthesize),
and shows PilatusImageViewer for action=1/2 (display).

Original: lib/Synthesizer/ImageSynthesizer.py (GUI layer)
Copyright (c) SAXS Team, KEK-PF
"""

import re
import logging
import numpy as np

import pilatus_synthesizer._keklib.our_messagebox as MessageBox
from pilatus_synthesizer._keklib.execution_window.threads_connector import ThreadsConnector
from pilatus_synthesizer._keklib.execution_window.action_window import ActionWindow

from pilatus_synthesizer.core.image_synthesizer import exec_single_synthesis
from pilatus_synthesizer.core.pilatus_image import PilatusImage, pixel_rounded_shift
from pilatus_synthesizer.config.preferences import get_preference
from pilatus_synthesizer.config.settings import get_setting, get_mask
from pilatus_synthesizer.config.development import get_devel_info
from pilatus_synthesizer.__init__ import version_string

logger = logging.getLogger(__name__)


class _SilentConnector:
    """Drop-in connector for auto-run: logs to Python logger, no window."""

    def is_cancelled(self) -> bool:
        return False

    def put_cancelled(self) -> None:
        pass

    def put_log(self, message: str) -> None:
        logger.info('[auto] %s', message)

    def put_progress(self, value: int) -> None:
        pass

    def run_in_thread(self, func, *args, **kwargs):
        import threading
        t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t


class ImageSynthesizer:
    """GUI-aware synthesizer tied to a parent Tk widget."""

    def __init__(self, window=None):
        self._window = window

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def execute(self, action: int, exec_array: list, confirm: bool = True) -> None:
        self._set_setting_info(action)

        if not exec_array:
            return

        if action < 3:
            if len(exec_array) > 1:
                MessageBox.showinfo(
                    'First Selection Notice',
                    'Only the first selection will be shown.')
            self._show_images(exec_array[0])
            return

        # action == 3: synthesize
        n = len(exec_array)
        s = 's' if n > 1 else ''
        if confirm and not MessageBox.askokcancel(
                'Confirmation',
                f'You are making synthesized images for {n} sample{s}. OK?'):
            return

        self._exec_array = exec_array
        logger.info('Preparing calculations with %s', version_string())

        if not confirm:
            # Auto-run: no window, background thread, log to Python logger only
            connector = _SilentConnector()
            connector.run_in_thread(self._exec_syntheses, connector)
            return

        connector = ThreadsConnector()
        win = ActionWindow(
            self._window,
            title='Execution Log',
            connector=connector,
            max_progress=sum(max(1, len(r[1]) - 1) for r in exec_array),
        )
        connector.run_in_thread(self._exec_syntheses, connector)
        win.wait_window(win)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_setting_info(self, action: int) -> None:
        self._action = action
        self._direction = get_setting('positive_direction')
        mask_obj = get_mask()
        self._mask_array = mask_obj.mask_array if mask_obj else None
        self._syn_method = get_preference('syn_method')
        self._min_ratio = get_devel_info('min_ratio')
        self._syn_flags = get_preference('syn_flags')
        self._postfix_adj = get_devel_info('postfix_adj')
        self._postfix_syn = get_preference('postfix_syn')
        self._algorithm = get_devel_info('adj_algorithm')
        self._adj_output = get_devel_info('adj_output') == 'YES'
        self._intermediate = get_devel_info('intermediate_results') == 'YES'

    def _show_images(self, exec_rec: list) -> None:
        from pilatus_synthesizer.gui.image_viewer import PilatusImageViewer

        sample_id = exec_rec[0]
        in_folder = get_setting('in_folder')
        syn_folder = get_setting('syn_folder')
        exec_rec_array = exec_rec[1]

        mask_array = None if self._action == 1 else self._mask_array
        exec_params = []

        o_file = exec_rec_array[0][0]
        if o_file:
            o_path = f'{in_folder}/{o_file}'
            o_pim = PilatusImage(o_path, mask_array or '')
            exec_params.append([o_file, o_pim.image_array()])

        for i, sub_rec in enumerate(exec_rec_array[1:], start=1):
            s_delta = [int(float(d) * 1000) for d in sub_rec[1]]
            i_delta = [pixel_rounded_shift(d) for d in s_delta]

            if self._action == 1:
                a_file = sub_rec[0]
                if a_file:
                    a_path = f'{in_folder}/{a_file}'
                    a_pim = PilatusImage(a_path)
                    a_im = a_pim.image_array()
                    exec_params.append([a_file, a_im])
            else:
                s_file = sub_rec[0]
                if s_file:
                    s_path = f'{in_folder}/{s_file}'
                    a_pim = PilatusImage(
                        s_path, self._mask_array or '',
                        s_delta[0], s_delta[1],
                        direction=self._direction,
                        algorithm=self._algorithm,
                    )
                    a_im = a_pim.image_array()
                    exec_params.append([f'{sample_id}_{i}_adj', a_im,
                                        i_delta[0], i_delta[1]])

            # Last sub_rec: also show the synthesized result if it exists
            if i == len(exec_rec_array) - 1:
                z_file = sub_rec[4]
                if z_file:
                    z_path = f'{syn_folder}/{z_file}'
                    try:
                        z_pim = PilatusImage(z_path)
                        exec_params.append([z_file, z_pim.image_array()])
                    except Exception:
                        pass

        self._viewer = PilatusImageViewer(self._action, sample_id, exec_params)

    def _exec_syntheses(self, connector: ThreadsConnector) -> None:
        in_folder = get_setting('in_folder')
        adj_folder = get_setting('adj_folder')
        syn_folder = get_setting('syn_folder')

        for exec_rec in self._exec_array:
            if connector.is_cancelled():
                connector.put_cancelled()
                return

            sample_id = exec_rec[0]
            exec_rec_array = exec_rec[1]
            num_changes = exec_rec[2] if len(exec_rec) > 2 else len(exec_rec_array) - 1

            base_rec = exec_rec_array[0]
            previous_im = None
            valid_value_sum_array = None
            valid_pixel_counter_array = None

            try:
                for i, sub_rec in enumerate(exec_rec_array[1:], start=1):
                    if connector.is_cancelled():
                        connector.put_cancelled()
                        return

                    fkey = '%s_%d' % (sample_id, i)
                    isfinal = (i == len(exec_rec_array) - 1)

                    counter_id = get_preference('detection_counter')
                    with_phrase = ''
                    if counter_id != 'None':
                        i_ratio = sub_rec[2] or 1.0
                        with_phrase = f' with {counter_id}-ratio {i_ratio:.5f}'

                    _b0 = base_rec[0] if isinstance(base_rec[0], str) else ''
                    org_file = re.sub(r'\.\w+$', '', _b0)
                    sft_file = re.sub(r'\.\w+$', '', sub_rec[0] or '')
                    syn_file = '%s%s' % (sample_id if isfinal else fkey,
                                        self._postfix_syn)

                    exec_seq_no = i
                    do_exec = (exec_seq_no >= 3 or
                               (self._syn_flags and
                                exec_seq_no < len(self._syn_flags) and
                                self._syn_flags[exec_seq_no]))

                    if do_exec and len(exec_rec_array) == num_changes:
                        logger.info('Synthesizing %-20s and %-20s into %-20s%s',
                                    org_file, sft_file, syn_file, with_phrase)
                        connector.put_log(
                            f'Synthesizing {org_file} + {sft_file} → {syn_file}{with_phrase}')

                        result = exec_single_synthesis(
                            sample_id, base_rec, fkey, sub_rec,
                            isfinal=isfinal,
                            mask_array=self._mask_array,
                            direction=self._direction,
                            in_folder=in_folder,
                            adj_folder=adj_folder if self._adj_output else None,
                            syn_folder=syn_folder,
                            syn_method=self._syn_method,
                            min_ratio=self._min_ratio,
                            adj_output=self._adj_output,
                            postfix_adj=self._postfix_adj,
                            postfix_syn=self._postfix_syn,
                            algorithm=self._algorithm,
                            intermediate_results=self._intermediate,
                            previous_im=previous_im,
                            valid_value_sum_array=valid_value_sum_array,
                            valid_pixel_counter_array=valid_pixel_counter_array,
                        )
                        previous_im = result['previous_im']
                        valid_value_sum_array = result['valid_value_sum_array']
                        valid_pixel_counter_array = result['valid_pixel_counter_array']
                        base_rec = [result['result_array']] + list(sub_rec[1:])
                    else:
                        logger.info('Skipping %-20s and %-20s', org_file, sft_file)
                        connector.put_log(f'Skipping {org_file} + {sft_file}')

                    connector.put_progress(i)

            except Exception:
                import traceback
                msg = traceback.format_exc()
                logger.exception("Error processing '%s'", sample_id)
                connector.put_log(f'ERROR in {sample_id}:\n{msg}')

        connector.put_log('Done!')
        logger.info('Done!')
