from dowel import LogOutput, Tabular


class NullOutput(LogOutput):
    """Dummy output to disable 'no logger output' warnings."""

    @property
    def types_accepted(self):
        """Accept all output types."""
        return (object, )

    def record(self, data, prefix=''):
        """Don't do anything."""
        if isinstance(data, Tabular):
            data.mark_all()
