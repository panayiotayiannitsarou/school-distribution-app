# app_v3.py – Πλήρης εφαρμογή κατανομής μαθητών με ασφάλεια και Βήματα 1 έως 6

SECURITY_CODE = "katanomi2025"

def validate_access():
    code = input("Εισάγετε κωδικό πρόσβασης: ").strip()
    if code != SECURITY_CODE:
        print("Μη εξουσιοδοτημένη πρόσβαση. Τερματισμός.")
        exit()

validate_access()

# ---- Helper Functions ----

def is_in_class(s_id, classes):
    return any(s_id in [s['id'] for s in cl] for cl in classes)

def has_conflict(student, cl):
    return any(conflict_id in [s['id'] for s in cl] for conflict_id in student.get('conflicts', []))

# ---- Βήμα 1: Παιδιά Εκπαιδευτικών ----
def assign_teacher_children(students, classes):
    teacher_children = [s for s in students if s['is_teacher_child']]
    num_classes = len(classes)
    distributed_ids = set()

    for i in range(min(num_classes, len(teacher_children))):
        child = teacher_children[i]
        classes[i].append(child)
        distributed_ids.add(child['id'])

    remaining = [s for s in teacher_children if s['id'] not in distributed_ids]
    for child in remaining:
        placed = False
        for cl in classes:
            for peer in cl:
                if peer['is_teacher_child'] and peer['id'] in child.get('friends', []) and child['id'] in peer.get('friends', []):
                    cl.append(child)
                    placed = True
                    break
            if placed: break
        if not placed:
            for cl in classes:
                for peer in cl:
                    if peer['is_teacher_child'] and peer['gender'] != child['gender']:
                        cl.append(child)
                        placed = True
                        break
                if placed: break
        if not placed:
            for cl in classes:
                cl.append(child)
                break

# ---- Βήμα 2: Φίλοι Παιδιών Εκπαιδευτικών ----
def assign_friends_of_teacher_children(students, classes):
    student_map = {s['id']: s for s in students}
    teacher_children_ids = [s['id'] for s in students if s['is_teacher_child']]

    for i, cl in enumerate(classes):
        teacher_kids_in_class = [s for s in cl if s['id'] in teacher_children_ids]
        if len(teacher_kids_in_class) >= 2:
            for tk in teacher_kids_in_class:
                for fid in tk.get('friends', []):
                    friend = student_map.get(fid)
                    if (friend and tk['id'] in friend.get('friends', []) and
                        not friend['is_teacher_child'] and not friend['is_lively'] and
                        not has_conflict(friend, cl) and not is_in_class(friend['id'], classes)):
                        cl.append(friend)

# ---- Βήμα 3: Ζωηροί ----
def assign_lively_students(students, classes):
    lively_students = [s for s in students if s['is_lively']]
    for student in lively_students:
        candidate_classes = []
        for i, cl in enumerate(classes):
            lively_count = sum(1 for s in cl if s['is_lively'])
            if lively_count >= 2: continue
            if any(s['id'] in student.get('friends', []) and student['id'] in s.get('friends', []) for s in cl):
                continue
            if has_conflict(student, cl): continue
            candidate_classes.append((i, cl, lively_count, len(cl)))
        if not candidate_classes:
            for cl in classes:
                if not has_conflict(student, cl):
                    cl.append(student)
                    break
        else:
            candidate_classes.sort(key=lambda x: (x[2], len([s for s in x[1] if s['gender'] == student['gender']]), x[3]))
            classes[candidate_classes[0][0]].append(student)

# ---- Βήμα 4: Παιδιά με Ιδιαιτερότητες ----
def assign_special_needs_students(students, classes):
    special_students = [s for s in students if s['is_special'] and not is_in_class(s['id'], classes)]
    for student in special_students:
        class_lively_counts = [(i, sum(1 for s in cl if s['is_lively'])) for i, cl in enumerate(classes)]
        min_lively = min(c for _, c in class_lively_counts)
        candidate_classes = [i for i, c in class_lively_counts if c == min_lively]
        final_classes = []
        for i in candidate_classes:
            cl = classes[i]
            if not has_conflict(student, cl):
                final_classes.append((i, cl))
        if final_classes:
            final_classes.sort(key=lambda x: (
                sum(1 for s in x[1] if s['is_special']),
                sum(1 for s in x[1] if s['gender'] == student['gender']),
                len(x[1])
            ))
            final_classes[0][1].append(student)

# ---- Βήμα 5: Χαμηλή Γλωσσική Επάρκεια ----
def assign_language_needs_students(students, classes, max_class_size=25):
    def get_class_index_of(student_id):
        for i, cl in enumerate(classes):
            if any(s['id'] == student_id for s in cl):
                return i
        return None

    def is_fully_mutual_friend(s, friend_id):
        friend = next((x for x in students if x['id'] == friend_id), None)
        return friend and s['id'] in friend.get('friends', [])

    def class_stats():
        return [(i, len(cl)) for i, cl in enumerate(classes)]

    def count_gender(cl, gender):
        return sum(1 for s in cl if s['gender'] == gender)

    language_students = [s for s in students if s['is_language_support'] and not is_in_class(s['id'], classes)]

    for student in language_students:
        placed = False
        for friend_id in student.get('friends', []):
            if not is_fully_mutual_friend(student, friend_id): continue
            class_index = get_class_index_of(friend_id)
            if class_index is not None:
                cl = classes[class_index]
                if not has_conflict(student, cl) and len(cl) < max_class_size:
                    cl.append(student)
                    placed = True
                    break
        if placed: continue

        candidate_classes = []
        for i, cl in enumerate(classes):
            if has_conflict(student, cl) or len(cl) >= max_class_size:
                continue
            lang_count = sum(1 for s in cl if s.get('is_language_support'))
            gender_count = count_gender(cl, student['gender'])
            candidate_classes.append((i, cl, lang_count, gender_count, len(cl)))
        if candidate_classes:
            candidate_classes.sort(key=lambda x: (x[2], x[3], x[4]))
            best_index = candidate_classes[0][0]
            classes[best_index].append(student)

# ---- Βήμα 6: Υπόλοιποι Μαθητές με Φίλους ----
def assign_remaining_students_with_friends(students, classes, max_class_size=25):
    """
    Τοποθετεί τα υπόλοιπα παιδιά με βάση τις πλήρως αμοιβαίες φιλίες (ζευγάρια και τριάδες),
    λαμβάνοντας υπόψη: όριο 25 μαθητών ανά τμήμα, διαφορά έως 1 μαθητή, ισορροπία φύλου και αποφυγή συγκρούσεων.
    """

    def is_in_class(s_id):
        return any(s_id in [s['id'] for s in cl] for cl in classes)

    def has_conflict(student, cl):
        return any(c in [s['id'] for s in cl] for c in student.get('conflicts', []))

    def get_student_by_id(s_id):
        return next((s for s in students if s['id'] == s_id), None)

    def class_stats():
        return [(i, len(cl)) for i, cl in enumerate(classes)]

    def class_gender_score(cl, group):
        gender = [s['gender'] for s in group]
        same_gender_count = sum(1 for s in cl if s['gender'] in gender)
        return same_gender_count

    def is_balanced_distribution():
        sizes = sorted(len(cl) for cl in classes)
        return sizes[-1] - sizes[0] <= 1

    def can_add_group(cl, group):
        return (
            len(cl) + len(group) <= max_class_size and
            all(not has_conflict(s, cl) for s in group)
        )

    unplaced = [s for s in students if not is_in_class(s['id'])]
    used_ids = set()

    # Ζευγάρια
    for s in unplaced:
        if s['id'] in used_ids:
            continue
        for f_id in s.get('friends', []):
            friend = get_student_by_id(f_id)
            if (friend and not is_in_class(friend['id']) and
                s['id'] in friend.get('friends', []) and
                friend['id'] not in used_ids):

                pair = [s, friend]
                # Βρες τμήμα με ισορροπία και διαθέσιμη θέση
                candidate_classes = []
                for i, cl in enumerate(classes):
                    if can_add_group(cl, pair):
                        gender_score = class_gender_score(cl, pair)
                        candidate_classes.append((i, cl, gender_score, len(cl)))
                if candidate_classes:
                    candidate_classes.sort(key=lambda x: (x[2], x[3]))  # ισορροπία φύλου και μέγεθος
                    best_class = candidate_classes[0][1]
                    best_class.extend(pair)
                    used_ids.update([s['id'], friend['id']])
                break

    # Τριάδες
    unplaced = [s for s in students if not is_in_class(s['id'])]
    for a in unplaced:
        if a['id'] in used_ids:
            continue
        for b_id in a.get('friends', []):
            b = get_student_by_id(b_id)
            if not b or b['id'] in used_ids or a['id'] not in b.get('friends', []):
                continue
            for c_id in a.get('friends', []):
                if c_id == b_id:
                    continue
                c = get_student_by_id(c_id)
                if (c and c['id'] not in used_ids and
                    a['id'] in c.get('friends', []) and
                    b['id'] in c.get('friends', []) and
                    c_id in b.get('friends', [])):

                    trio = [a, b, c]
                    candidate_classes = []
                    for i, cl in enumerate(classes):
                        if can_add_group(cl, trio):
                            gender_score = class_gender_score(cl, trio)
                            candidate_classes.append((i, cl, gender_score, len(cl)))
                    if candidate_classes:
                        candidate_classes.sort(key=lambda x: (x[2], x[3]))
                        best_class = candidate_classes[0][1]
                        best_class.extend(trio)
                        used_ids.update([x['id'] for x in trio])
                    break
            if a['id'] in used_ids:
                break

# --- Παράδειγμα εκτέλεσης ---
students = []
classes = [[] for _ in range(2)]

assign_teacher_children(students, classes)
assign_friends_of_teacher_children(students, classes)
assign_lively_students(students, classes)
assign_special_needs_students(students, classes)
assign_language_needs_students(students, classes)
assign_remaining_students_with_friends(students, classes)

def assign_remaining_students_without_friends(students, classes, max_class_size=25):
    """
    Τοποθετεί μαθητές που δεν έχουν φίλους ή δεν συμμετέχουν σε αμοιβαίες φιλίες,
    και δεν έχουν τοποθετηθεί ακόμα. Λαμβάνονται υπόψη πληθυσμός, φύλο και συγκρούσεις.
    """

    def is_in_class(s_id):
        return any(s_id in [s['id'] for s in cl] for cl in classes)

    def has_conflict(student, cl):
        return any(cid in [s['id'] for s in cl] for cid in student.get('conflicts', []))

    def gender_balance_score(cl, gender):
        return sum(1 for s in cl if s['gender'] == gender)

    remaining_students = [s for s in students if not is_in_class(s['id'])]

    for student in remaining_students:
        candidate_classes = []
        for i, cl in enumerate(classes):
            if len(cl) >= max_class_size:
                continue
            if has_conflict(student, cl):
                continue
            gender_score = gender_balance_score(cl, student['gender'])
            candidate_classes.append((i, cl, gender_score, len(cl)))

        if candidate_classes:
            # προτεραιότητα: λίγοι του ίδιου φύλου, μικρότερος πληθυσμός
            candidate_classes.sort(key=lambda x: (x[2], x[3]))
            best_class = candidate_classes[0][1]
            best_class.append(student)

assign_remaining_students_without_friends(students, classes)