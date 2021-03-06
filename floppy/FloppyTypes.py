FLOPPYTYPES = {}


class MetaType(type):
    def __new__(cls, name, bases, classdict):
        result = type.__new__(cls, name, bases, classdict)
        # result.__dict__['Input'] = result._addInput
        FLOPPYTYPES[name] = result
        return result


class Type(object, metaclass=MetaType):
    color = (255, 255, 255)

    @staticmethod
    def debugInfoGetter(obj):
        raise AttributeError


class Atom(Type):
    color = (204, 0, 204)

    @staticmethod
    def checkType(instance):
        return instance

    @staticmethod
    def debugInfoGetter(obj):
        return obj.get_name


class Structure(Type):
    color = (36, 80, 222)

    @staticmethod
    def checkType(instance):
        return instance

    @staticmethod
    def debugInfoGetter(obj):
        return obj.get_name


class Number(Type):
    color = (13, 239, 199)

    @staticmethod
    def checkType(instance):
        return instance

    @staticmethod
    def debugInfoGetter(obj):
        return obj.get_name


class LongAtom(Type):
    color = (234, 106, 21)

    @staticmethod
    def checkType(instance):
        return instance

    @staticmethod
    def debugInfoGetter(obj):
        return obj.get_name