import cv2
import numpy as np
import sys
import os


def analyze_malaria(image_path, batch_mode=False):
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error : Impossible to read the image {image_path}")
        return True, None, 0

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_purple = np.array([110, 50, 50])
    upper_purple = np.array([160, 255, 255])
    mask = cv2.inRange(hsv_image, lower_purple, upper_purple)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    detected_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 20:
            detected_count += 1
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    filename = os.path.basename(image_path)
    is_infected = detected_count > 0

    if detected_count > 1:
        print(f"[ALERT] {filename} : {detected_count} infections detected")
    elif detected_count == 1:
        print(f"[ALERT] {filename} : 1 infection detected")
    else:
        print(f"[OK] {filename} : No anomalies detected")

    cv2.putText(image, filename, (5, 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(image, f"Anomalies: {detected_count}", (5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    cv2.imshow("Resultat Analyse", image)
    key = cv2.waitKey(1) if batch_mode else cv2.waitKey(0)

    if key == ord('q'):
        return False, is_infected, detected_count
    return True, is_infected, detected_count


def print_analytics(stats):
    total = stats['total']
    infected = stats['infected']
    healthy = stats['healthy']
    errors = stats['errors']
    total_infections = stats['total_infections']

    print("\n" + "=" * 60)
    print("                    ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nGLOBAL STATISTICS:")
    print(f"   ☆ Images analysed  : {total}")
    print(f"   ☆ Reading errors   : {errors}")
    print(f"\nDETECTION RESULTS:")
    print(f"   ☆ Images infected  : {infected}")
    print(f"   ☆ Images healthy   : {healthy}")
    print(f"   ☆ Total infections : {total_infections}")

    if total > 0:
        valid_total = total - errors
        if valid_total > 0:
            infected_pct = (infected / valid_total) * 100
            healthy_pct = (healthy / valid_total) * 100
            print(f"\nPERCENTAGES:")
            print(f"   ☆ Infection rate   : {infected_pct:.1f}%")
            print(f"   ☆ Healthy rate     : {healthy_pct:.1f}%")

            bar_len = 40
            infected_bar = int(bar_len * infected_pct / 100)
            healthy_bar = bar_len - infected_bar
            print(f"\n   [{'🔴' * infected_bar}{'🟢' * healthy_bar}]")

    print("\n" + "=" * 60)


def process_path(path, batch_mode=False):
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tif')

    stats = {
        'total': 0,
        'infected': 0,
        'healthy': 0,
        'errors': 0,
        'total_infections': 0
    }

    if os.path.isdir(path):
        print(f"\n--- Analyse du dossier : {path} ---\n")
        files = sorted(os.listdir(path))

        for file in files:
            if file.lower().endswith(valid_extensions):
                full_path = os.path.join(path, file)
                stats['total'] += 1

                keep_going, is_infected, infection_count = analyze_malaria(full_path, batch_mode)

                if is_infected is None:
                    stats['errors'] += 1
                elif is_infected:
                    stats['infected'] += 1
                    stats['total_infections'] += infection_count
                else:
                    stats['healthy'] += 1

                if not keep_going:
                    print("\n User interruption.")
                    break

        if stats['total'] > 0:
            print_analytics(stats)

    elif os.path.isfile(path):
        print(f"\n --- Analyse du fichier unique --- \n")
        _, is_infected, infection_count = analyze_malaria(path)
        if is_infected:
            print(f"\nResult: INFECTED IMAGE ({infection_count} infection(s))")
        elif is_infected is not None:
            print(f"\nResult: HEALTHY IMAGE")

    else:
        print(f"Error : The path '{path}' does not exist.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <file_or_folder_path> [--batch]")
        print("  --batch : analyse all of the images in the folder at once")
        return

    path_arg = sys.argv[1]
    batch_mode = '--batch' in sys.argv
    process_path(path_arg, batch_mode)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()