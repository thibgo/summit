from pyscm.scm import SetCoveringMachineClassifier as scm

from ..monoview.monoview_utils import CustomRandint, CustomUniform, \
    BaseMonoviewClassifier

# Author-Info
__author__ = "Baptiste Bauvin"
__status__ = "Prototype"  # Production, Development, Prototype


# class DecisionStumpSCMNew(scm, BaseEstimator, ClassifierMixin):
#     """docstring for SCM
#     A hands on class of SCM using decision stump, built with sklearn format in order to use sklearn function on SCM like
#     CV, gridsearch, and so on ..."""
#
#     def __init__(self, model_type='conjunction', p=0.1, max_rules=10, random_state=42):
#         super(DecisionStumpSCMNew, self).__init__(model_type=model_type, max_rules=max_rules, p=p, random_state=random_state)
#         # self.model_type = model_type
#         # self.p = p
#         # self.max_rules = max_rules
#         # self.random_state = random_state
#         # self.clf = scm(model_type=self.model_type, max_rules=self.max_rules, p=self.p, random_state=self.random_state)
#
#     # def fit(self, X, y):
#     #     print(self.clf.model_type)
#     #     self.clf.fit(X=X, y=y)
#     #
#     # def predict(self, X):
#     #     return self.clf.predict(X)
#     #
#     # def set_params(self, **params):
#     #     for key, value in iteritems(params):
#     #         if key == 'p':
#     #             self.p = value
#     #         if key == 'model_type':
#     #             self.model_type = value
#     #         if key == 'max_rules':
#     #             self.max_rules = value
#
#     # def get_stats(self):
#     #     return {"Binary_attributes": self.clf.model_.rules}


class SCM(scm, BaseMonoviewClassifier):

    def __init__(self, random_state=None, model_type="conjunction",
                 max_rules=10, p=0.1, **kwargs):
        super(SCM, self).__init__(
            random_state=random_state,
            model_type=model_type,
            max_rules=max_rules,
            p=p
        )
        self.param_names = ["model_type", "max_rules", "p", "random_state"]
        self.distribs = [["conjunction", "disjunction"],
                         CustomRandint(low=1, high=15),
                         CustomUniform(loc=0, state=1), [random_state]]
        self.classed_params = []
        self.weird_strings = {}

    def canProbas(self):
        """Used to know if the classifier can return label probabilities"""
        return True

    def getInterpret(self, directory, y_test):
        interpretString = "Model used : " + str(self.model_)
        return interpretString


def formatCmdArgs(args):
    """Used to format kwargs for the parsed args"""
    kwargsDict = {"model_type": args.SCM_model_type,
                  "p": args.SCM_p,
                  "max_rules": args.SCM_max_rules}
    return kwargsDict


def paramsToSet(nIter, randomState):
    paramsSet = []
    for _ in range(nIter):
        paramsSet.append(
            {"model_type": randomState.choice(["conjunction", "disjunction"]),
             "max_rules": randomState.randint(1, 15),
             "p": randomState.random_sample()})
    return paramsSet