import sklearn
import sklearn.datasets


categories = ['alt.atheism', 'soc.religion.christian', 'comp.graphics', 'sci.med']

twenty_trains = sklearn.datasets.load_files(
	"C:\\Users\\alexandre\\Documents\\Informatique\\IA\\TP\\MachineLearning",
	description=None,
	categories=categories,
	load_content=True,
	shuffle=True,
	encoding='latin-1',
	decode_error='strict',
	random_state=42
)

print(twenty_trains.target_names)
print(len(twenty_trains.filenames))

print("\n".join(twenty_trains.data[0].split("\n")[:3]))