# https://stackoverflow.com/questions/45514353/pyopengl-perspective-projection
import OpenGL, PIL, pygame, numpy, pyrr, math, sys, os

from OpenGL.GL import *
from PIL import Image
from pyrr import Matrix44, Vector4, Vector3, Quaternion

VERT_DATA = numpy.array([0.5, 0.5, 0.0,
                         0.5, -0.5, 0.0,
                        -0.5, -0.5, 0.0,
                        -0.5, 0.5, 0.0],
                        dtype="float32")

COLOR_DATA = numpy.array([1.0, 0.0, 0.0, 1.0,
                          0.0, 1.0, 0.0, 1.0,
                          0.0, 0.0, 1.0, 1.0,
                          0.0, 1.0, 1.0, 1.0],
                          dtype="float32")

TEXTURE_COORD_DATA = numpy.array([0.5, 0.5,
                                  0.5, -0.5,
                                 -0.5, -0.5,
                                 -0.5, 0.5],
                                 dtype="float32")

INDICES = numpy.array([0, 1, 3,
                       1, 2, 3],
                       dtype="int32")

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

class GLProgram:
    def __init__(self):
        self.gl_program = glCreateProgram()
        self.mvp_matrix = self.projection()
        self.shaders()
        self.gl_buffers()
        self.cube_model_matrix, self.cube_view_matrix, self.cube_proj_matrix = self.gl_translate(Vector3([1.0, 1.0, 1.0]), 45.0, Vector3([0.5, 0.5, 0.5]))
        self.cube_mvp = self.gl_translate3(Vector3([1.0, 1.0, 1.0]), -45.0, Vector3([0.5, 0.5, 0.5]))

    def gl_texture(self, texture_path):
        return 0

    def gl_buffers(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.pos_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
        glBufferData(GL_ARRAY_BUFFER, VERT_DATA, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        self.text_coord_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.text_coord_vbo)
        glBufferData(GL_ARRAY_BUFFER, TEXTURE_COORD_DATA, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        self.pos_ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.pos_ebo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.pos_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDICES, GL_STATIC_DRAW)

        self.brick_texture = self.gl_texture("check.jpg")

    def shaders(self):
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

        with open("VertexShader.vert", "r") as vert_file:
            vert_source = vert_file.read()
        with open("FragmentShader.frag", "r") as frag_file:
            frag_source = frag_file.read()

        glShaderSource(vertex_shader, vert_source)
        glShaderSource(fragment_shader, frag_source)

        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(vertex_shader)
            print ("Compilation Failure for " + vertex_shader + " shader:\n" + info_log)

        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(fragment_shader)
            print ("Compilation Failure for " + fragment_shader + " shader:\n" + info_log)

        glAttachShader(self.gl_program, vertex_shader)
        glAttachShader(self.gl_program, fragment_shader)

        glLinkProgram(self.gl_program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def projection(self):
        scale_matrix = pyrr.matrix44.create_from_scale(Vector3([1, 1, 1]))
        rot_matrix = Matrix44.identity()
        trans_matrix = pyrr.matrix44.create_from_translation(Vector3([1, 1, 0]))

        model_matrix = scale_matrix * rot_matrix * trans_matrix
        view_matrix = pyrr.matrix44.create_look_at(numpy.array([4, 3, 3]), numpy.array([1, 1, 0]), numpy.array([0, 1, 0]))
        proj_matrix = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280/720, 0.1, 1000.0)
        mvp_matrix = proj_matrix * view_matrix * model_matrix

        return mvp_matrix
    def gl_translate(self, translation, rotation, scale):
        # Vector3([1.0, 1.0, 1.0]), 45.0, Vector3([0.5, 0.5, 0.5])
        trans_matrix = pyrr.matrix44.create_from_translation(translation)
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_y_rotation(rotation))
        scale_matrix = numpy.transpose(pyrr.matrix44.create_from_scale(scale))

        model_matrix = scale_matrix * rot_matrix * trans_matrix
        view_matrix = pyrr.matrix44.create_look_at(numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32"))
        proj_matrix = pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0)

        return model_matrix, view_matrix, proj_matrix

    def gl_translate2(self, translation, rotation, scale):
        trans_matrix = pyrr.matrix44.create_from_translation(translation)
        rot_matrix = pyrr.matrix44.create_from_y_rotation(rotation)
        scale_matrix = pyrr.matrix44.create_from_scale(scale)

        model_matrix = numpy.matmul(numpy.matmul(scale_matrix,rot_matrix),trans_matrix)
        view_matrix = pyrr.matrix44.create_look_at(numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32"))
        proj_matrix = pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0)
        m = numpy.matmul(numpy.matmul(model_matrix,view_matrix),proj_matrix)

        return m
    def gl_translate3(self, translation, rotation, scale):
        trans_matrix = numpy.transpose(pyrr.matrix44.create_from_translation(translation))
        rot_matrix = numpy.transpose(pyrr.matrix44.create_from_y_rotation(rotation))
        scale_matrix = numpy.transpose(pyrr.matrix44.create_from_scale(scale))

        model_matrix = numpy.matmul(numpy.matmul(trans_matrix,rot_matrix),scale_matrix)
        view_matrix = numpy.transpose(pyrr.matrix44.create_look_at(numpy.array([2.0, 2.0, 3.0], dtype="float32"),
            numpy.array([0.0, 0.0, 0.0], dtype="float32"),
            numpy.array([0.0, 1.0, 0.0], dtype="float32")))
        proj_matrix = numpy.transpose(pyrr.matrix44.create_perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0))
        m = numpy.matmul(numpy.matmul(proj_matrix,view_matrix),model_matrix)

        return numpy.transpose(m)

    def display(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.gl_program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.brick_texture)
        texture_uniform = glGetUniformLocation(self.gl_program, "the_texture")
        glUniform1i(texture_uniform, 0)

        trans_uniform = glGetUniformLocation(self.gl_program, "mvp")
        glUniformMatrix4fv(trans_uniform, 1, GL_FALSE, self.cube_mvp)
        #model_location = glGetUniformLocation(self.gl_program, "model")
        #glUniformMatrix4fv(model_location, 1, GL_FALSE, self.cube_model_matrix)
        #view_location = glGetUniformLocation(self.gl_program, "view")
        #glUniformMatrix4fv(view_location, 1, GL_FALSE, self.cube_view_matrix)
        #proj_location = glGetUniformLocation(self.gl_program, "proj")
        #glUniformMatrix4fv(proj_location, 1, GL_FALSE, self.cube_proj_matrix)
        glBindVertexArray(self.vao)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glUseProgram(0)

def main():
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption("3D Graphics")
    pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.OPENGL)
    clock = pygame.time.Clock()
    gl = GLProgram()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)
        gl.display()
        pygame.display.flip()

if __name__ == "__main__":
    main()








    # Using this Vertex Shader:

    # version 330 core

    layout(location=0) in vec3
    position;
    layout(location=1) in vec2
    text_coord;

    out
    vec2
    final_text_coord;

    uniform
    mat4
    mvp;

    void
    main()
    {
        gl_Position = mvp * vec4(position, 1.0);
    final_text_coord = text_coord;
    }

    #Using this Fragment Shader:

    # version 330 core

    in vec2
    final_text_coord;

    out
    vec4
    frag_color;

    uniform
    sampler2D
    the_texture;

    void
    main()
    {
        frag_color = vec4(1, 0, 0, 1);
    }