class Question:
    def __init__(self, question_id, question, answers):
        self.question_id = question_id
        self.text = question
        self.answers = []
        self.correct = None
        for answer in answers:
            answer_id = len(self.answers)
            if isinstance(answer, str):
                self.answers.append(answer)
            elif isinstance(answer, dict) and len(answer) == 1 and 'correct' in answer and self.correct is None:
                self.answers.append(answer['correct'])
                self.correct = answer_id
            else:
                raise ValueError(f'Invalid answers in question {question_id}: {answers}')