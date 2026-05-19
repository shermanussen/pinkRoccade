### INFO
This program uses python to store municipality data from the CBS in a PostgreSQL 16 database, according to PinkRoccades Local Government assessment. The assessment explicitly requires the program to be able to store data from multiple years (in my case 2023 and 2024).

### INSTALL
To be able to run this program, Docker is required.
Make sure directory 'datasets' is created in project root, where the municipality data-files live. The paths of the data-files must be preceded by 'data/':
If the data-file is stored in 'datasets/2023_file.gpkg', then the directory in config.json becomes: '/data/2023_file.gpkg'.
After building docker container, the container can be ran (
    $docker compose up --build
)

### Explanation
In creating this project, I've tried to make it ready for new versions of the data and for new datasets for the upcoming years.

#### Initialization
By building the Docker container, an initial setup for the postgreSQL-db is created. Two schemas are created: raw and production, to distinguish between the 'data-lake' (the unfiltered input-data) and the production-ready data.
Inside this production schema, six tables are created: two for each data-layer: production.data_layer and production.master_data_layer. The reason for the master_data_layer is to quickly see which row corresponds to the row of interest. Because of the data_layer_codes being able to change, it is necessary to have a id_master which tells us to which entity that row belongs. Example:
Let's say municipality Amsterdam in 2023 has 'gemeentecode' = 123. In 2024, this 'gemeentecode' may have changed to 'ABC', even though the domain/area of the municipality hasn't changed (situation of 'indelingswijziging_wijken_en_buurten' = 2); in this scenario it's difficult/resource-intense to see that these different entries belong to the same municipality. The id_master is a solution to that issue.

#### Extraction
In trying to store this data, I've decided to first extract the data into a GeoDataFrame, ensuring that the 'geometry'-property of the dataset is handled correctly. The data_extractor in this case only extracts .gpkg-files. The extraction-method can be replaced by any type of extractor, as long as its return-value is a dictionary containing the name of the layer (gemeenten, wijken, buurten) and its corresponding GeoDataFrame.

#### Transformation
In the transformation-step, duplicated entries are removed, given that only one row of data should correspond to one entity (one row per municipality/area/neighbourhood per year (looking at the same data_layer-code and year combination)). This is done by comparing each row to each duplicate. In this comparison, every column is compared, and the faulty values (which is denoted by -99997, 99997, 99995 or 99991, according to the documentation) are replaced by the duplicates correct value. If both values are faulty, the faulty value remains.
After that, the faulty values are being replaced with None (Which will be mapped to NULL when loading into PostgreSQL-db)

#### Loading
The last step, loading the data into the database, I first check whether all the necessary columns are available. If in the next year/dataset new columns are introduced, these are included in the db. Then, the data-to-be-stored is stored in a temporary table; here the data is prepared for production (this is faster than doing that in Python).
Next, the id_master is being set to each row of the temporary database based on the following logic:
If indelingswijziging_wijken_en_buurten = 1, take the id_master of the same data_layer_code (e.g. gemeentecode) of the given year (see if the dataset was already loaded). If not, take the id_master of the preceding year with this data_layer_code. If nothing is found, take the value of 'master_id_seq' instead.
If indelingswijziging_wijken_en_buurten = 2, check whether this year has a geometry which is equal to the geometry of the row (has the row already been read) If so, take the id_master already in the system. If not, check whether the preceding year had a geometry which is equal to the geometry of this row. If so: take that id_master. If nothing is found: take the value of 'master_id_seq' instead.
Else: 'master_id_seq'. 
The idea of master_id_seq is that it's being incremented for every unique entity: if it cannot be matched with an existing entity, its value is increased and appointed to this row.
If, in a renewed version the matching to previous years is changed (for example indelingswijziging_wijken_en_buurten becomes 2 instead of 1), the mapping will not be corrected for this new version by reloading the new version into the database. This to ensure that id_master will not be renewed when the base year (in our example 2023) gets reloaded again.

#### Testing
If I would have had more time, I would've explicitly created test-cases for at least all of the indelingswijziging_wijken_en_buurten-scenarios, for each data_layer.