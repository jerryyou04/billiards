#include "phylib.h"

//Part 1 functions (Constructors)

// Function to create a new still ball.
phylib_object* phylib_new_still_ball( unsigned char number,
                                    phylib_coord *pos ) {
    phylib_object * new_phyobject = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_phyobject == NULL) {
        return NULL; // Checking if NULL
    }

    new_phyobject->type = PHYLIB_STILL_BALL; // still ball type
    new_phyobject->obj.still_ball.pos = *pos; // set characteristics to passed values
    new_phyobject->obj.still_ball.number = number;

    return new_phyobject;
}

//Function to create a new rolling ball.
phylib_object *phylib_new_rolling_ball( unsigned char number,
                                        phylib_coord *pos,
                                        phylib_coord *vel,
                                        phylib_coord *acc ) {
    
    if (pos == NULL || vel == NULL || acc == NULL) {
        return NULL; // Needs all of these values to be present.
    }
    phylib_object * new_phyobject = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_phyobject == NULL) {
        return NULL; // checking for failed memory allocation.
    }

    new_phyobject->type = PHYLIB_ROLLING_BALL; //give characteristics from function
    new_phyobject->obj.rolling_ball.number = number;
    new_phyobject->obj.rolling_ball.pos = *pos;
    new_phyobject->obj.rolling_ball.vel = *vel;
    new_phyobject->obj.rolling_ball.acc = *acc;

    return new_phyobject;    
}

// Function for a new hole.
phylib_object *phylib_new_hole( phylib_coord *pos ) {
    phylib_object * new_phyobject = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_phyobject == NULL) {
        return NULL; // failed to allocate memory
    }

    new_phyobject->type = PHYLIB_HOLE; // set correct characteristics
    new_phyobject->obj.hole.pos = *pos;

    return new_phyobject;
}

//Function for new horizontal cushion.
phylib_object *phylib_new_hcushion( double y ) {
    phylib_object * new_phyobject = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_phyobject == NULL) {
        return NULL; // failed to allocate memory
    }   

    new_phyobject->type = PHYLIB_HCUSHION; // give characteristics to hcushion
    new_phyobject->obj.hcushion.y = y;

    return new_phyobject;
}

//Function for new vertical cushion.
phylib_object *phylib_new_vcushion( double x ) {
    phylib_object * new_phyobject = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_phyobject == NULL) {
        return NULL;
    }   

    new_phyobject->type = PHYLIB_VCUSHION; // give characteristics to vcushion
    new_phyobject->obj.vcushion.x = x;

    return new_phyobject;
}

//Creating a new table
phylib_table *phylib_new_table( void ) {
    phylib_table * new_phytable = (phylib_table *)malloc(sizeof(phylib_table));

    if (new_phytable == NULL) {
        return NULL;
    }

    new_phytable->time = 0.0; // set time to 0 as it just started

    new_phytable->object[0] = phylib_new_hcushion(0.0); // initialize the cushions in their respective places
    new_phytable->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    new_phytable->object[2] = phylib_new_vcushion(0.0);
    new_phytable->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    phylib_coord hole_positions[6] = { // initialize holes in the correct position
        {0.0, 0.0},  
        {0.0, PHYLIB_TABLE_LENGTH / 2},  
        {0.0, PHYLIB_TABLE_LENGTH},  
        {PHYLIB_TABLE_WIDTH, 0.0},  
        {PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH / 2},  
        {PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}  
    };

    for (int i = 4; i < 10; i++) {
        new_phytable->object[i] = phylib_new_hole(&hole_positions[i-4]);
    }

    //set remaining objects to null (the balls)
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++) {
        new_phytable->object[i] = NULL;
    }

    return new_phytable;
}

// PART II (UTILITY FUNCTIONS)


/*
This function should allocate new memory for a phylib_object. Save the address of that
object at the location pointed to by dest, and copy over the contents of the object from the
location pointed to by src. Hint, you can use memcpy to make this a one-step operation that
works for any type of phylib_object. If src points to a location containing a NULL pointer,
then the location pointed to by dest should be assigned the value of NULL
*/

//Function to copy one object to another
void phylib_copy_object( phylib_object **dest, phylib_object **src ) {
    if (*src == NULL){
        *dest = NULL; // set dest to null if source is also null
        return;
    }

    *dest = (phylib_object *) malloc(sizeof(phylib_object));

    if (*dest == NULL) {
        return; // failed to allocate
    }   

    memcpy(*dest,*src, sizeof(phylib_object)); // full copy
}

/*
This function should allocate memory for a new phylib_table, returning NULL if the malloc
fails. Then the contents pointed to by table should be copied to the new memory location and
the address returned.
*/
phylib_table *phylib_copy_table( phylib_table *table ) {
    if (table == NULL) {
        return NULL;
    }
    phylib_table * new_table = (phylib_table *)malloc(sizeof(phylib_table));

    if (new_table == NULL) {
        return NULL;
    }

     //Copy contents over
    new_table->time = table->time;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        new_table->object[i] = NULL; // Initialize to NULL
        if (table->object[i] != NULL) {
            // Allocate memory for the new object and call copy object for each
            phylib_copy_object(&new_table->object[i], &table->object[i]);
            if (new_table->object[i] == NULL) {
                return new_table;
            }
        }
    }
    return new_table;
}

/*
This function should iterate over the object array in the table until it finds a NULL pointer. It
should then assign that pointer to be equal to the address of object. If there are no NULL
pointers in the array, the function should do nothing.
*/
void phylib_add_object( phylib_table *table, phylib_object *object ) {
    if (table == NULL || object == NULL) {
        return; // checking for NULL pointers
    }
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) { // Immediately adds object when it finds a null pointer and returns.
            table->object[i] = object;
            return;
        }
    }
}

/*
Frees memory for a table.
*/
void phylib_free_table( phylib_table *table ) {
    if (table == NULL) {
        return; // Check for NULL
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            free(table->object[i]);
            table->object[i] = NULL; // set pointer to null
        }
    }

    free(table);
}

// subtracts c2 from c1.
phylib_coord phylib_sub( phylib_coord c1, phylib_coord c2 ) {
    phylib_coord diff;

    diff.x = c1.x-c2.x;
    diff.y = c1.y-c2.y;

    return diff;
}

// Computes the length of a coordinate using pythogorean theorem without exp.
double phylib_length( phylib_coord c ) {
    double length = sqrt(c.x * c.x + c.y * c.y);
    return length;
}

//Does dot product of coordinate a and b.
double phylib_dot_product( phylib_coord a, phylib_coord b ) {
    double product_x = a.x * b.x;
    double product_y = a.y * b.y;
    return product_x + product_y;
}

//Calculates the distance between two objects.
double phylib_distance( phylib_object *obj1, phylib_object *obj2 ) {
    if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL) {
        return -1.0; // Object 1 should always be rolling + check for NULL
    }
    
    double distance; 
    //Depending on the type of object, finds the distance by finding difference and calculating length
    if (obj2->type == PHYLIB_ROLLING_BALL) {
        phylib_coord diff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos);
        distance = phylib_length(diff) - PHYLIB_BALL_DIAMETER;
    }
    else if (obj2->type == PHYLIB_STILL_BALL) {
        phylib_coord diff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos);
        distance = phylib_length(diff) - PHYLIB_BALL_DIAMETER;
    }
    else if (obj2->type == PHYLIB_HOLE) {
        phylib_coord diff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos);
        distance = phylib_length(diff) - PHYLIB_HOLE_RADIUS;
    }
    else if (obj2->type == PHYLIB_HCUSHION) {
        distance = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
    }
    else if (obj2->type == PHYLIB_VCUSHION) {
        distance = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
    }
    else {
        return -1.0; // returns -1.0 if not found
    }

    return distance;
}


//PART III

//This function updates a new phylib_object that represents the old phylib_object after it has rolled for a period of time
void phylib_roll( phylib_object *new, phylib_object *old, double time ) {
    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL || new == NULL || old == NULL) { // checks if at least one of them is rolling
        return;
    }

    // Update position
    new->obj.rolling_ball.pos.x = old->obj.rolling_ball.pos.x + old->obj.rolling_ball.vel.x * time + 0.5 * old->obj.rolling_ball.acc.x * time * time;
    new->obj.rolling_ball.pos.y = old->obj.rolling_ball.pos.y + old->obj.rolling_ball.vel.y * time + 0.5 * old->obj.rolling_ball.acc.y * time * time;

    // Update velocity
    new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + old->obj.rolling_ball.acc.x * time;
    new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + old->obj.rolling_ball.acc.y * time;

    // Check for change in sign of velocity (x direction)
    if ((old->obj.rolling_ball.vel.x > 0 && new->obj.rolling_ball.vel.x < 0) || (old->obj.rolling_ball.vel.x < 0 && new->obj.rolling_ball.vel.x > 0)) {
        new->obj.rolling_ball.vel.x = 0;
        new->obj.rolling_ball.acc.x = 0;
    }

    // Check for change in sign of velocity (y direction)
    if ((old->obj.rolling_ball.vel.y > 0 && new->obj.rolling_ball.vel.y < 0) || (old->obj.rolling_ball.vel.y < 0 && new->obj.rolling_ball.vel.y > 0)) {
        new->obj.rolling_ball.vel.y = 0;
        new->obj.rolling_ball.acc.y = 0;
    }
}

//This function handles a rolling_ball stopping.
unsigned char phylib_stopped( phylib_object *object ) {
    if (object == NULL || object->type != PHYLIB_ROLLING_BALL) {
        return 0; // NULL pointers and only handles rolling ball
    }

    double speed = phylib_length(object->obj.rolling_ball.vel);

    if (speed < PHYLIB_VEL_EPSILON ) { // transfers all characteristics
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos.x = object->obj.rolling_ball.pos.x;
        object->obj.still_ball.pos.y = object->obj.rolling_ball.pos.y;
        return 1;
    }

    return 0; // returns 0 if it should not be stopped
}

//This function handles a rolling ball hitting off of different types of objects.
void phylib_bounce(phylib_object **a, phylib_object **b) {
    if (a == NULL || *a == NULL || (*a)->type != PHYLIB_ROLLING_BALL || b == NULL || *b == NULL) {
        return; // Handle NULL pointers and ensure a is a ROLLING_BALL
    }

    switch ((*b)->type) {
        case PHYLIB_HCUSHION:
            // Reverse y velocity and y acceleration
            (*a)->obj.rolling_ball.vel.y = -((*a)->obj.rolling_ball.vel.y);
            (*a)->obj.rolling_ball.acc.y = -((*a)->obj.rolling_ball.acc.y);
            break;

        case PHYLIB_VCUSHION:
            // Reverse x velocity and x acceleration
            (*a)->obj.rolling_ball.vel.x = -((*a)->obj.rolling_ball.vel.x);
            (*a)->obj.rolling_ball.acc.x = -((*a)->obj.rolling_ball.acc.x);
            break;

        case PHYLIB_HOLE:
            free(*a);
            *a = NULL;
            break;  // Break after freeing to prevent further access

        case PHYLIB_STILL_BALL:
            (*b)->type = PHYLIB_ROLLING_BALL;
            (*b)->obj.rolling_ball.pos = (*b)->obj.still_ball.pos;
            (*b)->obj.rolling_ball.number = (*b)->obj.still_ball.number;
            // Initialize velocity and acceleration for the newly converted rolling ball
            (*b)->obj.rolling_ball.vel.x = 0.0;
            (*b)->obj.rolling_ball.vel.y = 0.0;
            (*b)->obj.rolling_ball.acc.x = 0.0;
            (*b)->obj.rolling_ball.acc.y = 0.0;
            // Continue to the ROLLING_BALL case

        case PHYLIB_ROLLING_BALL: {
            phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
            double length_r_ab = phylib_length(r_ab);

            // Avoid division by zero
            if (length_r_ab == 0.0) {
                break;
            }

            phylib_coord n = {r_ab.x / length_r_ab, r_ab.y / length_r_ab};
            phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);
            double v_rel_n = phylib_dot_product(v_rel, n);

            (*a)->obj.rolling_ball.vel.x -= v_rel_n * n.x;
            (*a)->obj.rolling_ball.vel.y -= v_rel_n * n.y;
            (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
            (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;

            // Update accelerations
            update_acceleration(a, PHYLIB_VEL_EPSILON, PHYLIB_DRAG);
            update_acceleration(b, PHYLIB_VEL_EPSILON, PHYLIB_DRAG);

            break;
        }
    }
}

//This is a helper method for bounce to update acceleration.
void update_acceleration(phylib_object **obj, double vel_epsilon, double drag) {
    if ((*obj)->type == PHYLIB_ROLLING_BALL) {
        double speed = phylib_length((*obj)->obj.rolling_ball.vel);
        if (speed > vel_epsilon) {
            (*obj)->obj.rolling_ball.acc.x = -((*obj)->obj.rolling_ball.vel.x / speed) * drag;
            (*obj)->obj.rolling_ball.acc.y = -((*obj)->obj.rolling_ball.vel.y / speed) * drag;
        } 
    }
}

//This function calculates the amount of rolling balls on the table.
unsigned char phylib_rolling( phylib_table *t ) {
    if (t == NULL) {
        return 0;
    }
    unsigned char counter = 0;
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
            counter++; // adds one if the current index is a rolling ball.
        }
    }
    return counter;
}

// Handles a segment of a pool shot (time)
phylib_table *phylib_segment(phylib_table *table) {
    if (table == NULL || phylib_rolling(table) == 0) {
        return NULL; // No rolling balls or table is NULL
    }

    phylib_table *segment = phylib_copy_table(table);
    if (segment == NULL) {
        return NULL; // Failed to copy table
    }

    for (double time = PHYLIB_SIM_RATE; time <= PHYLIB_MAX_TIME; time += PHYLIB_SIM_RATE) {
        segment->time += PHYLIB_SIM_RATE;
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            if (segment->object[i] != NULL && segment->object[i]->type == PHYLIB_ROLLING_BALL) {
                // Update ball position with the current time increment
                phylib_roll(segment->object[i], table->object[i], time);

            }
        }
        // Check for collisions
        for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
            // Check if the ball has stopped
            if (segment->object[j] != NULL && segment->object[j]->type == PHYLIB_ROLLING_BALL) {
                if (phylib_stopped(segment->object[j])) {
                    return segment;
                }
            }
            for(int k = 0; k < PHYLIB_MAX_OBJECTS; k++) {
                if (k != j && segment->object[j] != NULL) {
                    double distance = phylib_distance(segment->object[k], segment->object[j]);
                    if (distance < 0.0 && distance != -1.0) {
                        phylib_bounce(&segment->object[k], &segment->object[j]);
                        // Return the segment after the collision is handled
                        return segment; 
                    }
                }
            }
            
        }
    }

    return segment;
}

char *phylib_object_string( phylib_object *object )
{
    static char string[80];
    if (object==NULL)
    {
        snprintf( string, 80, "NULL;" );
        return string;
    }
    switch (object->type)
        {
        case PHYLIB_STILL_BALL:
            snprintf( string, 80,
            "STILL_BALL (%d,%6.1lf,%6.1lf)",
            object->obj.still_ball.number,
            object->obj.still_ball.pos.x,
            object->obj.still_ball.pos.y );
            break;
        case PHYLIB_ROLLING_BALL:
            snprintf( string, 80,
            "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
            object->obj.rolling_ball.number,
            object->obj.rolling_ball.pos.x,
            object->obj.rolling_ball.pos.y,
            object->obj.rolling_ball.vel.x,
            object->obj.rolling_ball.vel.y,
            object->obj.rolling_ball.acc.x,
            object->obj.rolling_ball.acc.y );
            break;
        case PHYLIB_HOLE:
            snprintf( string, 80,
            "HOLE (%6.1lf,%6.1lf)",
            object->obj.hole.pos.x,
            object->obj.hole.pos.y );
            break;
        case PHYLIB_HCUSHION:
            snprintf( string, 80,
            "HCUSHION (%6.1lf)",
            object->obj.hcushion.y );
            break;
        case PHYLIB_VCUSHION:
            snprintf( string, 80,
            "VCUSHION (%6.1lf)",
            object->obj.vcushion.x );
            break;
        }
    return string;
}


