import glob
import math
import os
from tkinter import filedialog
import pandas as pd
from ast import literal_eval


def check_distance(mouse_nose_coord, object_center, interaction_dist_pixel):
    """
    Checks if the mouse is within the interaction distance of the object
    :param mouse_nose_coord: The mouse's (x,y) nose coordinate
    :param object_center: center_x, center_y, radius
    :param interaction_dist_pixel: The interaction distince in pixel radius
    :return: A true or false value, depending if the condition is met
    """
    interaction_radius = interaction_dist_pixel + object_center[2]

    if ((mouse_nose_coord[0] - object_center[0])**2 + (mouse_nose_coord[1] - object_center[1])**2 <=
            interaction_radius**2):
        return True
    return False


def update_counters(first_col, second_col, object, dist_pix, total_frames_counter, total_sniffle_frames_counter,
                    current_sniffle_frame_counter, sniffle_counter, required_frames):
    """
    Updates all the frame counters if they satisfy the conditions
    :param first_col: The column corresponding to the x position of the mouse's nose
    :param second_col: The column corresponding to the y position of the mouse's nose
    :param object: The list of object coordinates
    :param dist_pix: The interaction distance in pixel radius
    :param total_frames_counter: The total amount of frames in the video
    :param total_sniffle_frames_counter: The total amount of sniffles frame for the mouse
    :param current_sniffle_frame_counter: The current amount of frames going towards the sniffle requirement
    :param sniffle_counter: The mouse's total sniffle counter
    :param required_frames: The amount of frames needed for a sniffle bout
    :return: An updated version of the total frame counter, the total sniffle frame counter, the current sniffle frame counter, and the sniffle counter
    """
    mouse_nose_coord = (float(first_col), float(second_col))
    # increment the total frame counter
    if not math.isnan(mouse_nose_coord[0]) and not math.isnan(mouse_nose_coord[1]):
        total_frames_counter += 1
    # if the condition is met, increase current and total sniffle counters
    if check_distance(mouse_nose_coord, object, dist_pix):
        current_sniffle_frame_counter += 1
        total_sniffle_frames_counter += 1
        consecutive = True
    else:
        consecutive = False

    # if the frames aren't consecutive, reset the counter
    if not consecutive:
        current_sniffle_frame_counter = 0
    # increase the sniffle counter once if the required frames is met
    if current_sniffle_frame_counter == required_frames:
        sniffle_counter += 1

    return total_frames_counter, total_sniffle_frames_counter, current_sniffle_frame_counter, sniffle_counter


def slr(object_conversion, left_object_inputs, right_object_inputs, time_inputs, video_inputs, exp_inputs):
    """
    A function that produces a CSV containing the total sniffles, total sniffle frames, total sniffle time, and percentage of sniffle frames and time
    :param object_conversion: A list of object measurements and interaction distance
    :param left_object_inputs: A list of left object coordinates
    :param right_object_inputs: A list of right object coordinates
    :param time_inputs: The interaction time requirement
    :param video_inputs: The frames per second for the video
    :param exp_inputs: The experimental time for each trial
    """
    # inches-pixel conversion
    object_pixel_radius = int(object_conversion[0].get())
    object_cm_radius = float(object_conversion[1].get())
    pixel_per_cm = object_pixel_radius / object_cm_radius
    mouse_interaction_dist_cm = float(object_conversion[2].get())
    distance_in_pixels = pixel_per_cm * mouse_interaction_dist_cm

    # left object center coordinate
    left_object_top = literal_eval(left_object_inputs[0].get())
    left_object_left = literal_eval(left_object_inputs[1].get())

    left_object = [left_object_top[0], left_object_left[1], object_pixel_radius]

    # right object center coordinate
    right_object_top = literal_eval(right_object_inputs[0].get())
    right_object_left = literal_eval(right_object_inputs[1].get())

    right_object = [right_object_top[0], right_object_left[1], object_pixel_radius]

    # time criteria
    time_criteria_ms = int(time_inputs.get())
    time_criteria_s = time_criteria_ms / 1000

    # video information
    video_fps = int(video_inputs.get())

    # experiment criteria
    trial_runtime_s = int(exp_inputs.get())
    # round down for the sake of simplicity because fractional frames aren't possible
    required_frames_for_sniffle = math.floor(video_fps * time_criteria_s)

    # finding directory
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    mouse_entry = dict()
    mouse_entry_missed = dict()

    for index, file in enumerate(files):
        df_csv = pd.read_csv(file, index_col=False)
        # left mouse counters
        left_current_sniffle_frame_counter, left_total_sniffle_frames, left_sniffle_counter, left_total_frames = 0, 0, 0, 0
        # right mouse counters
        right_current_sniffle_frame_counter, right_total_sniffle_frames, right_sniffle_counter, right_total_frames = 0, 0, 0, 0
        # left missed mouse counters
        left_missed_current_sniffle_frame_counter, left_missed_total_sniffle_frames, left_missed_sniffle_counter, left_missed_total_frames = 0, 0, 0, 0
        # right missed mouse counters
        right_missed_current_sniffle_frame_counter, right_missed_total_sniffle_frames, right_missed_sniffle_counter, right_missed_total_frames = 0, 0, 0, 0
        # other counters
        mouse_counter = 1

        # iterate through all the rows and update the counters
        for row in df_csv[3:].itertuples():
            left_total_frames, left_total_sniffle_frames, \
            left_current_sniffle_frame_counter, left_sniffle_counter = update_counters(row[14], row[15], left_object,
                                                                                       distance_in_pixels,
                                                                                       left_total_frames,
                                                                                       left_total_sniffle_frames,
                                                                                       left_current_sniffle_frame_counter,
                                                                                       left_sniffle_counter,
                                                                                       required_frames_for_sniffle)
            right_total_frames, right_total_sniffle_frames, \
            right_current_sniffle_frame_counter, right_sniffle_counter = update_counters(row[2], row[3],
                                                                                         right_object,
                                                                                         distance_in_pixels,
                                                                                         right_total_frames,
                                                                                         right_total_sniffle_frames,
                                                                                         right_current_sniffle_frame_counter,
                                                                                         right_sniffle_counter,
                                                                                         required_frames_for_sniffle)
            left_missed_total_frames, left_missed_total_sniffle_frames, \
            left_missed_current_sniffle_frame_counter, left_missed_sniffle_counter = update_counters(row[2], row[3],
                                                                                                     left_object,
                                                                                                     distance_in_pixels,
                                                                                                     left_missed_total_frames,
                                                                                                     left_missed_total_sniffle_frames,
                                                                                                     left_missed_current_sniffle_frame_counter,
                                                                                                     left_missed_sniffle_counter,
                                                                                                     required_frames_for_sniffle)
            right_missed_total_frames, right_missed_total_sniffle_frames, \
            right_missed_current_sniffle_frame_counter, right_missed_sniffle_counter = update_counters(row[14], row[15],
                                                                                                       right_object,
                                                                                                       distance_in_pixels,
                                                                                                       right_missed_total_frames,
                                                                                                       right_missed_total_sniffle_frames,
                                                                                                       right_missed_current_sniffle_frame_counter,
                                                                                                       right_missed_sniffle_counter,
                                                                                                       required_frames_for_sniffle)

        if left_sniffle_counter <= left_missed_sniffle_counter:
            left_sniffle_counter = left_missed_sniffle_counter
            left_total_sniffle_frames = left_missed_total_sniffle_frames
        if right_sniffle_counter <= right_missed_sniffle_counter:
            right_sniffle_counter = right_missed_sniffle_counter
            right_total_sniffle_frames = right_missed_total_sniffle_frames

        # update information for each mouse
        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [left_sniffle_counter,
                                                                                   left_total_sniffle_frames,
                                                                                   left_total_sniffle_frames / video_fps,
                                                                                   left_total_sniffle_frames / left_total_frames * 100,
                                                                                   (
                                                                                           left_total_sniffle_frames / video_fps) / trial_runtime_s * 100]

        mouse_counter += 1
        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [right_sniffle_counter,
                                                                                   right_total_sniffle_frames,
                                                                                   right_total_sniffle_frames / video_fps,
                                                                                   right_total_sniffle_frames / right_total_frames * 100,
                                                                                   (
                                                                                           right_total_sniffle_frames / video_fps) / trial_runtime_s * 100]

    sniffle_df = pd.DataFrame.from_dict(mouse_entry, orient='index',
                                        columns=['Total Sniffles', 'Total Sniffle Frames',
                                                 'Total Sniffle Time in Seconds',
                                                 'Percentage of Sniffle Frames', 'Percentage of Sniffle Time'])

    # save to csv
    save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
    sniffle_df.to_csv(save_file_path)


def make_slr_buttons(tk, root):
    """
    Creates the UI for the social interaction functionality
    :param tk:
    :param root:
    """
    slr_object_pixel_label = tk.Label(root, text='Enter object radius in pixels:')
    slr_object_pixel_label.grid(row=0, column=0)
    slr_object_pixel_entry = tk.Entry(root, width=30, justify='center')
    slr_object_pixel_entry.grid(row=0, column=1)

    slr_object_cm_label = tk.Label(root, text='Enter object radius in cm:')
    slr_object_cm_label.grid(row=1, column=0)
    slr_object_cm_entry = tk.Entry(root, width=30, justify='center')
    slr_object_cm_entry.grid(row=1, column=1)

    slr_interaction_dist_label = tk.Label(root, text='Enter interaction distance in cm:')
    slr_interaction_dist_label.grid(row=2, column=0)
    slr_interaction_dist_entry = tk.Entry(root, width=30, justify='center')
    slr_interaction_dist_entry.grid(row=2, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=3, column=0)

    conversion_details = [slr_object_pixel_entry, slr_object_cm_entry, slr_interaction_dist_entry]

    slr_object_left_t_label = tk.Label(root, text='Enter left-object top coordinates as (x,y):')
    slr_object_left_t_label.grid(row=4, column=0)
    slr_object_left_t_entry = tk.Entry(root, width=30, justify='center')
    slr_object_left_t_entry.grid(row=4, column=1)

    slr_object_left_l_label = tk.Label(root, text='Enter left-object left coordinates as (x,y):')
    slr_object_left_l_label.grid(row=4, column=0)
    slr_object_left_l_entry = tk.Entry(root, width=30, justify='center')
    slr_object_left_l_entry.grid(row=4, column=1)

    spacer_btn_2 = tk.Label(root, text='')
    spacer_btn_2.grid(row=8, column=0)

    left_object_details = [slr_object_left_t_entry, slr_object_left_l_entry]

    slr_object_right_t_label = tk.Label(root, text='Enter left-object top coordinates as (x,y):')
    slr_object_right_t_label.grid(row=4, column=0)
    slr_object_right_t_entry = tk.Entry(root, width=30, justify='center')
    slr_object_right_t_entry.grid(row=4, column=1)

    slr_object_right_l_label = tk.Label(root, text='Enter left-object left coordinates as (x,y):')
    slr_object_right_l_label.grid(row=4, column=0)
    slr_object_right_l_entry = tk.Entry(root, width=30, justify='center')
    slr_object_right_l_entry.grid(row=4, column=1)

    spacer_btn_3 = tk.Label(root, text='')
    spacer_btn_3.grid(row=13, column=0)

    right_object_details = [slr_object_right_t_entry, slr_object_right_l_entry]

    slr_interaction_time_label = tk.Label(root, text='Enter the interaction time in ms:')
    slr_interaction_time_label.grid(row=14, column=0)
    slr_interaction_time_entry = tk.Entry(root, width=30, justify='center')
    slr_interaction_time_entry.grid(row=14, column=1)

    slr_video_fps_label = tk.Label(root, text='Enter the video fps:')
    slr_video_fps_label.grid(row=15, column=0)
    slr_video_fps_entry = tk.Entry(root, width=30, justify='center')
    slr_video_fps_entry.grid(row=15, column=1)

    slr_exp_time_label = tk.Label(root, text='Enter the experiment trial time in seconds:')
    slr_exp_time_label.grid(row=16, column=0)
    slr_exp_time_entry = tk.Entry(root, width=30, justify='center')
    slr_exp_time_entry.grid(row=16, column=1)

    slr_csv_btn = tk.Button(root, text='Make SI CSV',
                           command=lambda: slr(conversion_details, left_object_details, right_object_details,
                                               slr_interaction_time_entry, slr_video_fps_entry, slr_exp_time_entry))
    slr_csv_btn.grid(row=18, column=0, columnspan=2)